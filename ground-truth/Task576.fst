module Task576

// [576] Write a function to check whether a list is a sublist of another or not

let sub_array_at #a (s t: Seq.seq a) (i: nat) : prop =
  i + Seq.length s <= Seq.length t /\
    (forall (j: nat). j < Seq.length s ==>
        Seq.index s j == Seq.index t (i + j))

let sub_array #a (s t: Seq.seq a) : prop =
    exists (i: nat). sub_array_at s t i

let is_sub_array_at (#a: eqtype) (s t: Seq.seq a) (i: nat { i + Seq.length s <= Seq.length t }) :
        b:bool { b <==> sub_array_at s t i } =
    let rec check_until (k: nat { k <= Seq.length s /\ i + k <= Seq.length t }) :
            b:bool { b <==> (forall (j:nat). j < k ==> Seq.index s j == Seq.index t (i + j)) } =
        if k = 0 then
            true
        else
            let k = k - 1 in
            if Seq.index s k = Seq.index t (i + k) then
                check_until k
            else
                false in
    check_until (Seq.length s)

let is_sub_array (#a: eqtype) (s t: Seq.seq a) : b:bool { b <==> sub_array s t } =
    let rec check_until (k: nat { k + Seq.length s <= Seq.length t }) :
            b:bool { b <==> (exists (i: nat). i <= k /\ sub_array_at s t i) } =
        if is_sub_array_at s t k then
            true
        else if k = 0 then
            false
        else
            check_until (k - 1) in
    if Seq.length s > Seq.length t then
        false
    else
        check_until (Seq.length t - Seq.length s)

let test1: squash (is_sub_array (Seq.seq_of_list[1;4;3;5]) (Seq.seq_of_list[1;2]) == false) = ()
let test2: squash (is_sub_array (Seq.seq_of_list[1;2;1]) (Seq.seq_of_list[1;2;1]) == true) = ()
let test3: squash (is_sub_array (Seq.seq_of_list[1;0;2;2]) (Seq.seq_of_list[2;2;0]) == false) = ()

let test1_spec: squash (~ (sub_array (Seq.seq_of_list[1;4;3;5]) (Seq.seq_of_list[1;2]))) = ()
let test2': squash (sub_array (Seq.seq_of_list[1;2;1]) (Seq.seq_of_list[1;2;1])) = ()
let test3_spec: squash (is_sub_array (Seq.seq_of_list[1;0;2;2]) (Seq.seq_of_list[2;2;0]) == false) = ()
