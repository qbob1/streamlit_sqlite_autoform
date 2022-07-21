from os import getuid
import streamlit as st
import sqlite_utils
from default_mappings import default_inputs, default_values
import random

class SqliteAutoform:
    """
    lazydocs: ignore
    """

    def __init__(
        self,
        table,
        id=None,
        mappings={'inputs': default_inputs, 'values': default_values},
        submit=None
    ):
        self.table = table
        self.schema = table.columns
        self.mappings = mappings
        self.input_state = self.init_input_state(
        ) if id is None else self.table.get(id)
        self.id = id
        self.submit = submit if submit is not None else self.submit

    def render(self):
        with st.form(str(getuid())):
            for key in self.schema:
                # is pk, shouldn't be editable
                if key.is_pk > 0:
                    continue
                self.input_state[key.name] = self.mappings['inputs'][key.type.lower()](
                    label=key.name, value=self.input_state[key.name], key=str(getuid()))
            self.submit() if st.form_submit_button(label="Submit") else None

    def init_input_state(self):
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
            return st.exception(e)
        finally:
            st.success('Successfully inserted a new row')
