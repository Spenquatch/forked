1. **Clean slate & scaffold demo fork**

   ```bash
   # remove any prior demo repos (adjust name if you keep multiple)
   python - <<'PY'
   import pathlib, shutil
   for name in ['demo-feature-run', 'demo-feature-run-origin.git', 'demo-feature-run-upstream.git']:
       path = pathlib.Path(name)
       if path.exists():
           shutil.rmtree(path)
   PY

   ./scripts/setup-demo-repo.sh demo-feature-run
   cd demo-feature-run
   ```

   The helper script provisions upstream/origin remotes plus the patch branches
   `patch/contract-update` and `patch/service-logging`.

2. **Install / update Forked CLI (editable)**

   Run this once from the repository root (outside the demo fork) if you
   haven’t already:

   ```bash
   python -m pip install -e .
   ```

3. **Initialise the fork**

   ```bash
   forked init
   ```

   This fetches upstream, creates `trunk`, writes `forked.yml`, and enables
   `rerere` + diff3 merge style.

4. **Author feature-aware `forked.yml`**

   Update the generated config so it includes patch order, features, overlays,
   and sentinel rules:

   ```yaml
   patches:
     order:
       - patch/contract-update
       - patch/service-logging
   guards:
     sentinels:
       must_match_upstream:
         - "api/contracts/**"
   features:
     contract_update:
       patches:
         - patch/contract-update
       sentinels:
         must_match_upstream:
           - "api/contracts/**"
     service_logging:
       patches:
         - patch/service-logging
       sentinels:
         must_diverge_from_upstream:
           - "branding/**"
   overlays:
     dev:
       features: [contract_update, service_logging]
     observability-only:
       features: [service_logging]
   ```

   > Tip: keep a copy of this file handy or park it on a patch branch if you
   > plan to run multiple builds—`forked build` hard-resets `trunk` to
   > `upstream/main`.

5. **Confirm feature wiring**

   ```bash
   forked feature status
   ```

   You should see both feature names with their patch slices “1 ahead / 0
   behind”.

6. **Build overlay from profile + provenance**

    ```bash
    forked build --overlay dev --skip-upstream-equivalents
    git notes --ref=refs/notes/forked-meta show overlay/dev
    tail -n1 .forked/logs/forked-build.log
    ```

    Expect the build summary to list both patches, report zero skipped commits
    (unless you added upstream equivalents), and the git note/log entry to list
    `features=["contract_update","service_logging"]`.

7. **Guard should fail in block mode**

   ```bash
   forked guard --overlay overlay/dev --mode block
   echo $?  # 2 when sentinel trips
   jq '.violations.sentinels.must_match_upstream' .forked/report.json
   ```

8. **Guard override success path**

   ```bash
   git checkout overlay/dev
   git commit --allow-empty -m $'override paperwork\n\nForked-Override: sentinel'
   git checkout trunk
   forked guard --overlay overlay/dev --mode require-override
   jq '.override, .features' .forked/report.json
   ```

   The guard run should exit `0`, report `override.source == "commit"`, and set
   `override.applied == true` while exposing the overlay’s feature list.

9. **Status command regression + JSON contract**

   ```bash
   forked status --latest 2
   forked status --json --latest 3 | jq '.status_version, .patches, [.overlays[].selection.source]'
   ```

   Confirm the human-friendly table still renders, and the JSON output reports
   `status_version: 1`, ahead/behind counts, and overlay selections sourced from
   provenance (`"selection.source": "provenance-log"`).

10. **JSON fallback behaviour**

   ```bash
   mv .forked/logs/forked-build.log .forked/logs/forked-build.log.bak
   git notes --ref=refs/notes/forked-meta remove overlay/dev
   forked status --json --latest 3 | jq 'map(select(.name==\"overlay/dev\"))[0].selection'
   mv .forked/logs/forked-build.log.bak .forked/logs/forked-build.log
   forked build --overlay dev --skip-upstream-equivalents  # restore provenance
   ```

   You should see the CLI warn about missing provenance and return
   `"selection.source": "derived"` with resolver metadata. Re-run the build to
   put the log/note back for subsequent steps.

11. **Test include/exclude filters**

    ```bash
    forked build --overlay dev --exclude patch/service-logging --id dev-minus
    ```

    The build should only cherry-pick `patch/contract-update` and note the
    exclusion in the selection filters.

12. **Ad-hoc feature selection**

    ```bash
    forked build --features service_logging \
        --include patch/contract-update \
        --id combo \
        --skip-upstream-equivalents
    ```

    This exercises the resolver’s feature list + include override path, and it
    should still populate provenance for the combined selection.

13. **Create and inspect new feature slices**

    ```bash
    git add forked.yml .gitignore && git commit -m "chore: configure forked"
    forked feature create checkout --slices 2
    forked feature status
    ```

    The new feature appears with `patch/checkout/01` and `/02` marked as
    “merged” until they diverge from `trunk`.

14. **Cleanup (optional)**

    ```bash
    git worktree prune
    rm -rf .forked
    cd ..
    ```

    Remove the demo directories when you’re done or keep them for further
    experimentation.
