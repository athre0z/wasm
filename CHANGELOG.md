### v1.0 -> v1.1

- Many minor improvements and support for MVP WASM
    - Added decoding support for MVP name section
    - Added `format_function`, for formatting whole functions
    - Improved `wasmdump` command-line tool 

- Slight rework of meta info visibility
    - Renamed `_data_meta` -> `_decoder_meta`
    - Added getters `get_{meta,decoder_meta}` to `StructureData`