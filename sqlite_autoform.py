from os import getuid
import streamlit as st
import sqlite_utils
from streamlit_sqlite_autoform.default_mappings import default_inputs, default_values, default_cast_map

class SqliteAutoform:
    """
    lazydocs: ignore
    """
    def __init__(
        self,
        table: any,
        id : int = None,
        mappings : dict  = {'inputs': default_inputs, 'values': default_values, 'cast':default_cast_map},
        submit : callable = None
    ):
        self.table = table
        self.schema = table.columns
        self.mappings = mappings
        self.id = id
        self.submit = submit if submit is not None else self.submit
        self.render_map = {}
        self.input_state = {}
        self.init_render_mapping()

    def init_render_mapping(self):
        self.record = None if self.id is None else self.table.get(self.id)

        for key in self.schema: 
            self.render_map[key.name.lower()] = self.mappings['inputs'][key.type.lower()]
            self.input_state[key.name.lower()] =  self.record[key.name] if self.record is not None else self.mappings['values'][key.type.lower()]

    def edit_container(self):
        for key in self.schema:
            with st.expander(key.name+" Configuration"):
                st.text_input(label = "Renderer", value = self.render_map[key.name].__name__, key=f'{key.name}-render-fn')
                st.write(self.render_map[key.name].__func__.__qualname__)
                st.text_input(label = "Casting Function", value = self.mappings['cast'][key.type.lower()].__name__ , key=f'{key.name}-cast-fn')
                st.write(dir(self.mappings['cast']))
                st.button('Save', key=f'{key.name}-save')

    def render(self):
        Form, Edit = st.tabs(["Form", "Edit"])
        with Form:
            with st.form(str(getuid())):
                for key in self.schema:
                    try:
                        # is pk, shouldn't be editable
                        if key.is_pk > 0:
                            continue
                        self.input_state[key.name.lower()] = self.render_map[key.name.lower()](
                            label=key.name, value=default_cast_map[key.type.lower()](self.input_state[key.name]), key=str(getuid()))
                    except Exception as e:
                        st.write(f'error rendering {key.name} {key.type}')
                        st.exception(e)

                self.submit() if st.form_submit_button(label="Submit") else None
        
        with Edit:
            self.edit_container()

    def init_input_state(self) -> dict:
        acc = {}
        for column in self.schema:
            acc[column.name] = column.default_value if column.default_value is not None else self.mappings['values'][column.type.lower()]
        return acc

    def submit(self):
        try:
            if self.id is None:
                return self.table.insert(self.input_state)
            self.table.upsert(self.input_state, pk='id')
        except Exception as e:
            st.exception(e)
            return 
        finally:
            st.success('Successfully inserted a new row')
