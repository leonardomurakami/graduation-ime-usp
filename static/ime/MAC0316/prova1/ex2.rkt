#lang scheme
(define (sigma m n)
    (cond
        [(equal? m n) m]
        [(< n m) 0]
        [else (+ m (sigma (+ m 1) n))]
    )
)

(define (exp m n)
    (cond
        [(equal? n 0) 1]
        [(equal? n 1) m]
        [else (* m (exp m (- n 1)))]
    )
)

(define (log m n)
    (define (logaux m n l)
        (cond
            [(> (exp m (+ l 1)) n) l]
            [else (logaux m n (+ l 1))]
        )
    )
    (logaux m n 0)
)

(define (choose n k)
    (define (fat n)
        (cond
            [(equal? n 0) 1]
            [(equal? n 1) 1]
            [else (* n (fat (- n 1)))]
        )
    )
    (cond
        [(equal? k 0) 1]
        [(equal? n k) 1]
        [else (/ (fat n) (* (fat k)(fat (- n k))))]
    )
)

(define (choose-variant n k)
    (cond
        [(equal? k 0) 1]
        [(equal? n k) 1]
        [else (+ (choose-variant (- n 1) k) (choose-variant (- n 1) (- k 1)))]
    )
)

(sigma 1 5)
(exp 2 1)
(log 2 8)
(choose 10 2)
(choose-variant 10 2)