#lang scheme

(define combine (lambda (operation function null) 
    (lambda (lista) 
        (if (null? lista) 
            null
            (operation (function (car lista)) ((combine operation function null) (cdr lista)))
        )
    )
))

(define (cdr* l)
    (map (lambda (l) (cdr l)) l)
)

(define (max* l)
    ((combine
        max
        (lambda (x) x)
        -inf.0
    ) l)
)

(define (cons* l1 l2)
    (cons l1 (cons l2 '()))
)

(define (append* l1 l2)
    ((combine
        cons           
        (lambda (x) x)
        l2
    ) l1)
)

(define (addtoend s l)
    ((combine
        cons
        (lambda (x) x)
        (cons s '())
    ) l)
)

(define (reverse* l)
    ((combine
        addtoend
        (lambda (x) x)
        '()
    ) l)
)

(define (insert s l)
    (cond
        [(empty? l) (cons s l)]
        [(< s (car l)) (cons s l)]
        [else (cons (car l) (insert s (cdr l)))]
    )
)

(define (insertion-sort l)
    ((combine
        insert
        (lambda (x) x)
        '()
    ) l)
)

(define (mkpairfn x)
    (lambda (l)
        (map
            (lambda (lx)
                (cond 
                    [(list? lx) (cons x lx)]
                    [else (cons* x lx)]
                )
            )
            
        l)
    )
)

(cdr* '((a b c) (d e) (f)))

(max* '(3 1 4 1 5 9 2 6))

(append* '(1 2 3) '(4 5 6))

(cons* 1 2)

(addtoend 'a '(b c d))

(reverse* '(a b c d))

(insertion-sort '(2 3 1 9 7 4 3))

((mkpairfn 'a) '(() (b c) (d) ((e f))))