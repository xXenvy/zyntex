Welcome to Zyntex documentation!
=================================
Zyntex allows you to parse Zig source code directly from Python and exposes
high-level node objects (functions, variables, tests, etc.) for easy
inspection. Currently, it can parse Zig code written in version **0.14.1** -
the supported parsing version will be continuously updated in the future.

Zyntex uses Zig's `std` AST parser as a backend (via native bindings), which
provides fast and low-memory parsing.

**Be aware that the project is at a very early stage of development
and is actively being developed.**
For planned features and work in progress, see :ref:`Roadmap`.

---------------------------------------------------------------------------------------------


Getting started.
================
- **First steps:** :ref:`Installation` | :ref:`Examples` | :ref:`API Reference`.
- **Want to contribute?** See :ref:`Contributing`.
- **Need help?** Create a question on `Github Discussions. <https://github.com/xXenvy/zyntex/discussions>`_

.. toctree::
   :maxdepth: 3
   :hidden:

   installation
   examples/index
   roadmap
   contributing
   api/index
