# Step 19A - CI Validation

Added a GitHub Actions CI workflow that runs Ruff, the offline test suite,
release-asset validation, Bicep compilation, and a Docker image build.

CI runs for pull requests and pushes to `dev` and `main`.
