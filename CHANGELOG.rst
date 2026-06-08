=====================================
vitexus.multiflexi Release Notes
=====================================

.. contents:: Topics

v1.4.0
======

Minor Changes
-------------

- modules - Update all modules to comply with multiflexi-cli v2.5.6 syntax and the new Web5 interface.
- demo - Robust addon package installation, runtemplate creation for each installed package, and skipping of empty manifests.
- demo - Add configurable demo access and dynamic installation of all available MultiFlexi addon packages.
- eventsource - Improve event source management to match the updated CLI schema.
- packaging - Add AppStream metainfo XML and stock icon, installed via the Debian package.
- roles/multiflexi_server - Add configurable APT repository handling and align package upgrade tasks with the current CLI.
- docs - Refresh ``docs/multiflexi-cli.json`` schema documentation against multiflexi-cli v2.5.6.

New Modules
-----------

- vitexus.multiflexi.telemetry - Test OpenTelemetry metrics export in MultiFlexi.
- vitexus.multiflexi.user_company - Manage user-company assignments in MultiFlexi.
- vitexus.multiflexi.user_erasure - Manage GDPR user data erasure requests in MultiFlexi.
- vitexus.multiflexi.user_role - Manage user RBAC roles in MultiFlexi.

v1.3.1
======

Bugfixes
--------

- application - fix ``--deffile`` CLI option that does not exist; map both ``file`` and ``deffile`` module params to ``--file``.
- application - fix false ``changed`` on re-runs caused by comparing the provided file path against the system-installed ``deffile`` path stored in the API response; file path is now excluded from idempotency checks for existing applications.
- runtemplate - fix always-changed behaviour on re-runs; module now compares scalar fields and full config dict before deciding whether to update.

Minor Changes
-------------

- AGENTS.md added with guidance for AI coding agents covering module patterns, known CLI constraints, and local dev install workflow.

v1.3.0
======

Minor Changes
-------------

- artifact - Add new artifact module for managing job artifacts (list, get, save to file).
- docs - Update multiflexi-cli.json schema documentation with latest CLI interface.
- docs - Document requirement for multiflexi-cli version 2.2.0 or newer.
- roles/multiflexi_server - Update README with CLI version requirement.
- credential - Update credential module to support create and delete operations based on new multiflexi-cli schema.
- credential - Add support for credential_type_id parameter instead of deprecated type parameter.
- credential - Improve idempotency logic and error handling.

Breaking Changes / Porting Guide
---------------------------------

- credential - Parameter ``type`` replaced with ``credential_type_id`` to match CLI schema.
- credential - Parameters ``token`` and ``value`` removed from module interface.

New Modules
-----------

- vitexus.multiflexi.artifact - Manage job artifacts in MultiFlexi.
