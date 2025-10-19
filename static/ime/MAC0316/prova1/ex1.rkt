#lang scheme
(define (count x l)
    (cond
        [(empty? l) 0]
        [(equal? x (car l)) (+ 1 (count x (cdr l)))]
        [else (count x (cdr l))]
    )
)

(define (countall x l)
    (cond
        [(empty? l) 0]
        [(equal? x (car l)) (+ 1 (countall x (cdr l)))]
        [(list? (car l)) (+ (countall x (car l)) (countall x (cdr l)))]
        [else (countall x (cdr l))]
    )
)

(define (reverse l)
    (cond
        [(empty? l) '()]
        [else (append (reverse (cdr l)) (list (car l)))]
    )
)

(define (twist l)
    (cond
        [(empty? l) '()]
        [(list? (car l)) (append (twist (cdr l)) (list(twist (car l))))]
        [else (append (twist (cdr l)) (list (car l)))]
    )
)

(define (flatten l)
    (cond
        [(empty? l) '()]
        [(list? (car l)) (append (flatten (car l)) (flatten (cdr l)))]
        [else (append (list (car l)) (flatten (cdr l)))]
    )
)

(define (sublist l1 l2)
    (cond
        [(empty? l1) #t]
        [(and (empty? l2) (not (empty? l1))) '()]
        [(equal? (car l1) (car l2)) (sublist (cdr l1) (cdr l2))]
        [else (sublist l1 (cdr l2))]
    )
)

(define (contig-match l1 l2)
    (cond 
        [(empty? l1) #t]
        [(and (empty? l2) (not (empty? (l1)))) '()]
        [(equal? (car l1) (car l2)) (contig-match (cdr l1) (cdr l2))]
        [else '()]
    )
)

(define (contig-sublist l1 l2)
    (cond
        [(empty? l1) #t]
        [(and (empty? l2) (not (empty? l1))) '()]
        [(equal? (car l1) (car l2)) (contig-match (cdr l1) (cdr l2))]
        [else (contig-sublist l1 (cdr l2))]


    )
)


(count 'a '(a b a c a))
(countall 'a '(1 b a (c a) b a b b b a c (a b c a (b a c))))
(reverse '(a b a c a))
(twist '(a b (a b (a b c))))
(flatten '(a b (a b (a b) c)))
(sublist '(a b c) '(x a y b z c))
(contig-sublist '(a y) '(x a y b z c))