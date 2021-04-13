# CHANGELOG

## 2021-04-13
* Account list sorting...
  - Sorted by "name" as given in the `[account_map]` or ID if no `[account_map]` exists

## 2021-04-09
* Config code factored out to separate class
* Added the ability to define an `[account_map]` in the config file.
  - This allows you to map an account ID to an easily identifiable string
  - See the [README.rst](./README.rst) for details.
* Added the ability to define a color scheme in the config file in a `[colors]` section.
  - You can change the header & footer as well as defining alternating row colors
  - See the [README.rst](./README.rst) for details.
* You can now define a `username` option in the default (`[fedcred]`) section.
    - If defined, the user will not be prompted to enter it when run.
    - See the [README.rst](./README.rst) for details.
