#lang racket

(define combine (lambda (operation function null) 
    (lambda (lista) 
        (if (null? lista) 
            null
            (operation (function (car lista)) ((combine operation function null) (cdr lista)))
        )
    )
))

(define (*cdr l)
    (map cdr l)
)

(define (*max l)
    ((combine
        max
        (lambda (x) x)
        -inf.0
    ) l)
)

(define (append l s)
    ((combine
        cons
        (lambda (x) x)
        (cons s '())
    ) l)
)

(define (mkpairfn s l)
    (map (lambda (x) (cons s x)) l)
)


(*cdr '((1 2 3) (4 5) (6)))
(*max '(1 3 9 1 2 4 3))
(append '(1 2 3) 4)
(mkpairfn 'a '(() (b c) (d) ((e f))))