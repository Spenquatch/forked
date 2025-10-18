  1. Clean slate / scaffold

     rm -rf demo-forked demo-forked-origin.git demo-forked-upstream.git .forked
     ./scripts/setup-demo-repo.sh demo-forked
     cd demo-forked
     git checkout -b main origin/main
  2. Init Forked

     forked init
  3. Edit forked.yml once
      - Open forked.yml in your editor and set:

        patches:
          order:
            - patch/contract-update
            - patch/service-logging

        guards:
          sentinels:
            must_match_upstream:
              - "api/contracts/**"
     (No special commands—just save the file.)
  4. Build & reuse

     forked build --id test --auto-continue
     forked build --id test --auto-continue
  5. Run guard in block mode

     forked guard --overlay overlay/test --mode block
     echo $?    # prints 2 when the sentinel trips
  6. Check the report if you want

     cat .forked/report.json

     You’ll see api/contracts/v1.yaml under violations.sentinels.must_match_upstream.
