# Dataset Schema

Raw Monte Carlo JSON files under `data/raw/` use:

- `schema_version`: integer schema marker.
- `package_version`: package version string.
- `description`: run description from the config.
- `honesty`: scope disclaimer from the config.
- `config`: exact embedded run configuration.
- `runs`: one entry per beta value.

Each run contains:

- `beta`
- `seed_sequence`
- `plaquette_mean`
- `plaquette_std`
- `samples`

Each sample contains at least:

- `measurement`
- `plaquette`

Optional observable keys include `wilson_RxT` and `creutz_RxT`.
