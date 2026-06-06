# Step 19B - Immutable Agent Images

The controlled release uses the Git commit SHA as the default Container App
image tag. A caller may supply another immutable tag for a named learning
release.

The existing Container App deployment script remains the source of truth for
ACR build and Container App deployment.
