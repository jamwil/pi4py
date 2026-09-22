"""pi4py package."""


# Keep the Node.js helper lazy so ``python -m pi4py._nodejs`` does not import
# its module before runpy executes it.
def get_node_binary() -> str:
    """Return the path to Node.js bundled in the active Python environment."""
    from ._nodejs import get_node_binary as _get_node_binary

    return _get_node_binary()


__all__ = ["get_node_binary"]
