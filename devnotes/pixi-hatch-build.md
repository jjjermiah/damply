# Pixi Tasks for Hatch Build

The configuration for the Hatch build system is stored in the `config/hatch.toml` file. The `pyproject.toml` file contains the configuration for the Pixi build system.

## `config/hatch.toml`

The `[build]` section specifies the directory where the build artifacts are stored. 

The `[build.targets]` section specifies the packages to be built into a wheel distribution.

- The `packages` can be a list of multiple directories containing the package source code.

```toml
[build]
directory = "dist"

[build.targets]
wheel = { packages = [
  "../src/damply",
] }
```

## `pyproject.toml`

The `pyproject.toml` file contains the configuration for the Pixi build system.

The `[tool.pixi.feature.build.dependencies]` section specifies the dependencies required for the build feature.

The `[build-system]` section specifies the build system to be used and the build backend.

The `[tool.pixi.feature.build.tasks]` section contains the tasks for the build feature.

- The `build` task builds the package.

- The `publish-pypi` task publishes the package to the main PYPI repository.
  - This task depends on the `build` task.

- The `publish-test` task publishes the package to the TEST-PYPI repository.
  - This task depends on the `build` task.


```toml
[tool.pixi.feature.build.dependencies]
hatch = "*"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pixi.feature.build.tasks]
# Builds the package
build = { cmd = [
  "hatch",
  "build",
  "--clean",
], inputs = [
  "src",
  "config/hatch.toml",
  "pyproject.toml",
], outputs = [
  "dist/*",
], env = { HATCH_CONFIG = "config/hatch.toml" } }

# Publishes the package to the main PYPI repository, depends on the build task
publish-pypi = { cmd = [
  "hatch",
  "publish",
  "--yes",
  "--repo",
  "main",
], inputs = [
  "dist/*",
], depends-on = [
  "build",
], env = { HATCH_CONFIG = "config/hatch.toml" } }

# Publishes the package to the TEST-PYPI repository, depends on the build task
publish-test = { cmd = [
  "hatch",
  "publish",
  "--yes",
  "--repo",
  "test",
], inputs = [
  "dist/*",
], depends-on = [
  "build",
], env = { HATCH_CONFIG = "config/hatch.toml" } }
```