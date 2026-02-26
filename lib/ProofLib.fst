module ProofLib

(* Common definitions and lemmas for the proof agent *)

open FStar.List.Tot

(* Sorted predicate for lists *)
val sorted: list int -> bool
let rec sorted l = match l with
  | [] -> true
  | [_] -> true
  | x :: y :: rest -> x <= y && sorted (y :: rest)

(* Lemma: tail of sorted list is sorted *)
val sorted_tail: l:list int{sorted l /\ length l > 0} -> Lemma (sorted (tail l))
let sorted_tail l = ()

(* No duplicates predicate *)
val no_dups: #a:eqtype -> list a -> bool
let rec no_dups #a l = match l with
  | [] -> true
  | x :: xs -> not (mem x xs) && no_dups xs

(* Maximum of non-empty list *)
val max_list: l:list int{length l > 0} -> Tot int (decreases l)
let rec max_list l = match l with
  | [x] -> x
  | x :: xs -> let m = max_list xs in if x > m then x else m

(* Minimum of non-empty list *)
val min_list: l:list int{length l > 0} -> Tot int (decreases l)
let rec min_list l = match l with
  | [x] -> x
  | x :: xs -> let m = min_list xs in if x < m then x else m

(* Lemma: max >= min for non-empty list *)
val max_geq_min: l:list int{length l > 0} -> Lemma (max_list l >= min_list l)
let rec max_geq_min l = match l with
  | [_] -> ()
  | _ :: xs -> max_geq_min xs
