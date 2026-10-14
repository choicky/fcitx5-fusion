# Reverse-coupling review

## A. Recovery → ownership

D072 makes EAT an ownership responsibility and separately assigns P0-A the
recovery contract for an owned key when drain cannot reach terminal.  The
analysis therefore models recovery as obeying DP2 and producing DP6 terminal
accounting; it does not let backend failure or recovery convert an owned key to
a genuine PASS.  No reverse edge is required.  P0-A remains OPEN.  If its
future policy redefines the EAT contract, this gate must be revisited by owner
review; this preflight does not silently add that policy as accepted authority.

## B. Backend → Windows ownership

There is no such edge.  D072 explicitly states `TSF ownership != Fcitx
event.accepted()`.  Unexpected backend rejection of an already-owned key is a
contract/failure input to DP6, not a retroactive PASS.  Backend choice is not a
Windows correctness input.

## C. Host semantic state → document authority

The modeled direction is Host semantic proposal → Windows validation and
EditSession/materialization → document mutation/readback → APPLIED accounting.
Host state never asserts that mutation happened.  A failed or indeterminate
operation enters recovery/reconciliation and cannot be blindly retried.  Thus
there is no semantic-state/document-authority cycle in the accepted model.

## D. IPC/topology → correctness semantics

DP10 is an abstraction seam only.  Named Pipe, ALPC, RPC, and trust topology
remain P0-D OPEN.  The matrix gives topology no dependency into ownership,
EVENT/STATE/EFFECT, watermark, materialization, or PASS semantics.  A future
topology that requires changing those semantics would be an architecture
contradiction and must reopen the gate; none is required by D072.

## E. Backend choice → Windows correctness

DP13 is a replaceable v0.x reference profile.  Windows ownership, identity,
watermark, EditSession/readback, barriers, and recovery are defined at the TSF
boundary.  Replacing Fcitx5/LibIME may change semantic proposals or backend
adaptation, but does not require changing the Windows correctness core in this
analysis.
