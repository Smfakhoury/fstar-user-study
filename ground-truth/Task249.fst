module Task249
open FStar.List.Tot

//    [249] Write a function to find the intersection of two arrays.

let spec (#t: eqtype) (a b c : list t) =
    forall x. contains x c <==> contains x a /\ contains x b

let rec intersection_array (#t: eqtype) (a: list t) (b: list t) :
        c:list t { spec a b c } =
    match a with
    | [] -> []
    | a1::rest ->
        if contains a1 b then a1 :: intersection_array rest b else intersection_array rest b

let test1_spec : squash (spec [1; 2; 3; 5; 7; 8; 9; 10] [1; 2; 4; 8; 9] [1; 2; 8; 9]) = ()
let test2_spec : squash (spec [1; 2; 3; 5; 7; 8; 9; 10] [3; 5; 7; 9] [3; 5; 7; 9]) = ()
let test3_spec : squash (spec [1; 2; 3; 5; 7; 8; 9; 10] [10; 20; 30; 40] [10]) = ()

let test1_impl : squash (intersection_array [1; 2; 3; 5; 7; 8; 9; 10] [1; 2; 4; 8; 9] == [1; 2; 8; 9]) = ()
let test2_impl : squash (intersection_array [1; 2; 3; 5; 7; 8; 9; 10] [3; 5; 7; 9] == [3; 5; 7; 9]) = ()
let test3_impl : squash (intersection_array [1; 2; 3; 5; 7; 8; 9; 10] [10; 20; 30; 40] == [10]) = ()