#lang scheme

(define ints-pair
    (lambda (x)
        (cons x (
            lambda () (ints-pair (+ x 2))
        ))
    )
)

(define evens (ints-pair 0))

(car ((cdr evens)))