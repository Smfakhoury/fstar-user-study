module MaxDifference

(* Task 4: Returns the difference between the largest and smallest value in a given list *)

open FStar.List.Tot

(* SPECIFICATIONS *)

(* Maximum of non-empty list *)
val max_list: l:list int{length l > 0} -> Tot int (decreases l)
let rec max_list l = match l with
  | [x] -> x
  | x :: xs ->
    let m = max_list xs in
    if x > m then x else m

(* Minimum of non-empty list *)
val min_list: l:list int{length l > 0} -> Tot int (decreases l)
let rec min_list l = match l with
  | [x] -> x
  | x :: xs ->
    let m = min_list xs in
    if x < m then x else m

(* HELPER LEMMA *)

(* Lemma: max is always >= min *)
val max_geq_min: l:list int{length l > 0} -> Lemma (ensures max_list l >= min_list l) (decreases l)
let rec max_geq_min l = match l with
  | [_] -> ()
  | x :: xs -> max_geq_min xs

(* MAIN FUNCTION *)

val max_difference: l:list int{length l > 0} -> r:int{r >= 0}
let max_difference l =
  max_geq_min l;  (* invoke lemma *)
  max_list l - min_list l

(* TESTS *)
let test1 () = assert (max_difference [1;5;3;9;2] = 8)
let test2 () = assert (max_difference [5;5;5] = 0)
let test3 () = assert (max_difference [42] = 0)
