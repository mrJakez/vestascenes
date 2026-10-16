# CommonJS compatibility for the upstream security fix

Source: `decode-uri-component@0.5.0` from the npm registry
(https://github.com/SamVerschueren/decode-uri-component).

This is the upstream implementation and MIT license, with only
`export default function` changed to `module.exports = function`.
Version 0.5.0 fixes GHSA-vcc3-ghjq-m6fr. The older `query-string@7`
used by Vestaboard requires a callable CommonJS export; the upstream 0.5.0
package is ESM-only. The local dependency and npm override apply this fixed
implementation to every consumer without changing query-string's API.

Remove this compatibility copy and its dependency/override when Vestaboard
updates its query-string integration to support the upstream ESM package.
