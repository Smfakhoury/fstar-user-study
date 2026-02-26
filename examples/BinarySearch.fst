module BinarySearch

(* Task 1: Binary search implementation with verification *)

open FStar.Seq

(* SPECIFICATIONS *)

(* Sorted predicate for sequences *)
val sorted: s:seq int -> Tot bool (decreases (length s))
let rec sorted s =
  if length s <= 1 then true
  else index s 0 <= index s 1 && sorted (slice s 1 (length s))

(* Alternative sorted definition using forall *)
let sorted_spec (s: seq int) : prop =
  forall (i j: nat). i < j /\ j < length s ==> index s i <= index s j

(* HELPER LEMMA *)

(* Lemma: slicing a sorted sequence preserves sortedness *)
val sorted_slice: s:seq int -> i:nat -> j:nat{i <= j /\ j <= length s} ->
  Lemma (requires sorted s) (ensures sorted (slice s i j))
  [SMTPat (sorted (slice s i j))]
let sorted_slice s i j = admit ()  (* DEFER: will prove with induction *)

(* MAIN FUNCTION *)

(* Binary search with correctness specification *)
val binary_search: s:seq int{sorted s} -> target:int -> Tot (r:int{
  (r >= 0 ==> (r < length s /\ index s r = target)) /\
  (r = -1 ==> (forall (i:nat). i < length s ==> index s i <> target))
}) (decreases (length s))

let rec binary_search s target =
  if length s = 0 then -1
  else
    let mid = length s / 2 in
    let v = index s mid in
    if v = target then mid
    else if v < target then
      let result = binary_search (slice s (mid + 1) (length s)) target in
      if result >= 0 then result + mid + 1 else -1
    else
      binary_search (slice s 0 mid) target

(* TESTS using assert_norm for compile-time evaluation *)
let test_empty () = assert (binary_search (empty #int) 5 = -1)
let test_found () =
  let s = createL [1;2;3;4;5] in
  assert (binary_search s 3 = 2)
