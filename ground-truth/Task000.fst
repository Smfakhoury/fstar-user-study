module Task000
open FStar.List.Tot

// Given a sorted list xs and a value y, write the function binary_search which
// finds the index where y would need to be inserted in order to keep xs sorted,
// using binary search.

// making my life easy, we're only supporting integers here

let is_sorted (xs: list int) : prop =
    forall (i j: nat). i <= j /\ j < length xs ==> index xs i <= index xs j

let binary_search (xs: list int { is_sorted xs }) (y: int) :
        i:nat { i <= length xs
            /\ (forall (j:nat). j < i ==> index xs j < y)
            /\ (forall (j:nat). i <= j /\ j < length xs ==> index xs j >= y) } =
    let rec aux (m: nat) (n: nat { m <= n /\ n <= length xs }) :
            Tot (i:nat { m <= i /\ i <= n
                /\ (forall (j:nat). m <= j /\ j < i ==> index xs j < y)
                /\ (forall (j:nat). i <= j /\ j < n ==> index xs j >= y) })
            (decreases n - m) =
        if m = n then m
        else if m+1 = n then (if index xs m < y then n else m)
        else begin
            let k = m + (n - m) / 2 in
            let x = index xs k in
            if x < y then
                aux k n
            else
                aux m k
        end in
    aux 0 (length xs)

let test1 = assert (binary_search [1;3;7] 2 == 1)
let test2 = assert (binary_search [1;3;7] 10 == 3)
let test3 = assert (binary_search [1;3;7] (-10) == 0)
let test4 = assert (binary_search [1;3;3;7] 3 == 1)