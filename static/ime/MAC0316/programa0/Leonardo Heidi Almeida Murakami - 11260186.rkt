#lang plai-typed

#|
 | interpretador simples, com variáveis e funções
 |#

#| primeiro as expressões "primitivas", ou seja, diretamente interpretadas
 |#

(define-type ExprC
  [numC    (n : number)]
  [plusC   (l : ExprC) (r : ExprC)]
  [multC   (l : ExprC) (r : ExprC)]
  [divC    (l : ExprC) (r : ExprC)]
  [gtrC    (l : ExprC) (r : ExprC)]
  [andC    (l : ExprC) (r : ExprC)]
  [orC     (l : ExprC) (r : ExprC)]
  [xorC    (l : ExprC) (r : ExprC)]
  [equalC  (l : ExprC) (r : ExprC)]
  [notC    (e : ExprC)]
  [ifC     (cond : ExprC) (y : ExprC) (n : ExprC)]

  )
#| agora a linguagem aumentada pelo açúcar sintático
 | neste caso a operação de subtração e menus unário
 |#

(define-type ExprS
  [numS    (n : number)]
  [plusS   (l : ExprS) (r : ExprS)]
  [minusS  (l : ExprS) (r : ExprS)]
  [uminusS (e : ExprS)]
  [multS   (l : ExprS) (r : ExprS)]
  [divS    (l : ExprS) (r : ExprS)]
  [grtS    (l : ExprS) (r : ExprS)]
  [lessS   (l : ExprS) (r : ExprS)]
  [andS    (l : ExprS) (r : ExprS)]
  [orS     (l : ExprS) (r : ExprS)]
  [xorS    (l : ExprS) (r : ExprS)]
  [equalS  (l : ExprS) (r : ExprS)]
  [notS    (e : ExprS)]
  [ifS     (c : ExprS) (y : ExprS) (n : ExprS)]
  )


(define (desugar [as : ExprS]) : ExprC
  (type-case ExprS as
    [numS    (n)        (numC n)]
    [plusS   (l r)      (plusC (desugar l) (desugar r))]
    [minusS  (l r)      (plusC (desugar l) (multC (numC -1) (desugar r)))]  ; acucar sintatico: a - b = a + (-1 * b)
    [multS   (l r)      (multC (desugar l) (desugar r))]
    [divS    (l r)      (divC (desugar l) (desugar r))]
    [uminusS (e)        (multC (numC -1) (desugar e))]  ; menos unario como multiplicacao por -1
    [grtS    (l r)      (gtrC (desugar l) (desugar r))]
    [lessS   (l r)      (gtrC (desugar r) (desugar l))]  ; acucar sintatico: a < b = b > a
    [andS    (l r)      (andC (desugar l) (desugar r))] 
    [orS     (l r)      (orC (desugar l) (desugar r))] 
    [xorS    (l r)      (xorC (desugar l) (desugar r))]
    [equalS  (l r)      (equalC (desugar l) (desugar r))]
    [notS    (e)        (notC (desugar e))]
    [ifS     (c y n)    (ifC (desugar c) (desugar y) (desugar n))]

    ))


; We need a new value for the box
(define-type Value
  [numV  (n : number)] 
)


(define (interp [a : ExprC] ) : number
  (type-case ExprC a
    [numC (n) n]

    ;I left plusC without error-checking
    [plusC (l r)
             (+ (interp l) (interp r))]
    ;multC
    [multC (l r)
           (* (interp l) (interp r))]
    ;divC
    [divC (l r)
          (/ (interp l) (interp r))]
    ;gtrC
    [gtrC (l r) (if (> (interp l) (interp r)) 1 0)]
    ;andC
    [andC (l r) (if (= (interp l) 0) 0 (interp r))]
    ;orC
    [orC (l r) (if (= (interp l) 1) 1 (interp r))]
    ;xorC
    [xorC (l r) (let ([lval (interp l)] [rval (interp r)])
                  (if (and (= lval 0) (= rval 0)) 0 
                      (if (and (not (= lval 0)) (not (= rval 0))) 0 1)))]
    ;equalC
    [equalC (l r) (if (= (interp l) (interp r)) 1 0)]
    ;notC
    [notC (e) (if (= (interp e) 0) 1 0)]
    ; ifC serializes
    [ifC (c s n) (if (zero? (interp c))
                            (interp n  )
                            (interp s  ))]
   )
  )


; Parser with funny instructions for boxes
(define (parse [s : s-expression]) : ExprS
  (cond
    [(s-exp-number? s) (numS (s-exp->number s))]
    [(s-exp-list? s)
     (let ([sl (s-exp->list s)])
       (case (s-exp->symbol (first sl))
         [(+) (plusS (parse (second sl)) (parse (third sl)))]
         [(-) (minusS (parse (second sl)) (parse (third sl)))]
         [(*) (multS (parse (second sl)) (parse (third sl)))]
         [(/) (divS (parse (second sl)) (parse (third sl)))]
         [(~) (uminusS (parse (second sl)))]
         [(>) (grtS (parse (second sl)) (parse (third sl)))]
         [(<) (lessS (parse (second sl)) (parse (third sl)))]
         [(and) (andS (parse (second sl)) (parse (third sl)))]
         [(or) (orS (parse (second sl)) (parse (third sl)))]
         [(xor) (xorS (parse (second sl)) (parse (third sl)))]
         [(=) (equalS (parse (second sl)) (parse (third sl)))]
         [(not) (notS (parse (second sl)))]
         [(if) (ifS (parse (second sl)) (parse (third sl)) (parse (fourth sl)))]
        
         [else (error 'parse "invalid list input")]))]
    [else (error 'parse "invalid input")]))


; nao entendi se era para deixar com ou sem testes
; pois no email do Vinicius era dito para NAO enviar o arquivo final com esse codigo (codigo de teste)
