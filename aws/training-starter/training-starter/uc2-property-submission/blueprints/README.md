# Blueprint — you write this one

No starter file. Author the blueprint from the playbook's `output:` block
and the fields the sample documents actually contain.

Requirements:
- 30+ top-level properties
- at least 2 `definitions` used via `$ref` for repeating rows
- 4+ `validationRules`
- every optional field's `instruction` must say what to do when the
  field is absent — 'return null rather than guessing'

Compare against the UC1 blueprint for the shape, not the content.
