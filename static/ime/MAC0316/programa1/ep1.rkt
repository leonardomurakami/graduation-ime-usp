#lang plai-typed

#|
 | interpretador simples, sem variáveis ou funçõess
 |#

#| primeiro as expressões "primitivas", ou seja, diretamente interpretadas
 |#

(define-type ExprC
  [numC    (n : number)]
  [idC     (s : symbol)]
  [set!C   (s : symbol) (e : ExprC)]
  [letC    (s : symbol) (v : ExprC) (body : ExprC)]
  [plusC   (l : ExprC) (r : ExprC)]
  [multC   (l : ExprC) (r : ExprC)]
  [lamC    (arg : symbol) (body : ExprC)]
  [appC    (fun : ExprC) (arg : ExprC)]
  [ifC     (cond : ExprC) (y : ExprC) (n : ExprC)]
  [consC   (car : ExprC) (cdr : ExprC)]
  [carC    (pair : ExprC)]
  [cdrC    (pair : ExprC)]
  [beginC  (e1 : ExprC) (e2 : ExprC)]
  [lambda2C   (arg1 : symbol) (arg2 : symbol) (body : ExprC)]
  [app2C   (fun : ExprC) (arg1 : ExprC) (arg2 : ExprC)]
  [let*C   (v1 : symbol) (e1 : ExprC) (v2 : symbol) (e2 : ExprC) (body : ExprC)]
  [quoteC  (s : symbol)]
  [equalC  (l : ExprC) (r : ExprC)]
  )

#| agora a linguagem aumentada pelo açúcar sintático
 | neste caso a operação de subtração e menus unário
 |#

(define-type ExprS
  [numS    (n : number)]
  [idS     (s : symbol)]
  [set!S   (s : symbol) (v : ExprS)]
  [letS    (s : symbol) (v : ExprS) (body : ExprS)]
  [lamS    (arg : symbol) (body : ExprS)]
  [appS    (fun : ExprS) (arg : ExprS)]
  [plusS   (l : ExprS) (r : ExprS)]
  [bminusS (l : ExprS) (r : ExprS)]
  [uminusS (e : ExprS)]
  [multS   (l : ExprS) (r : ExprS)]
  [ifS     (c : ExprS) (y : ExprS) (n : ExprS)]
  [consS   (car : ExprS) (cdr : ExprS)]
  [carS    (pair : ExprS)]
  [cdrS    (pair : ExprS)]
  [beginS  (e1 : ExprS) (e2 : ExprS)]
  [let*S (v1 : symbol) (e1 : ExprS) 
            (v2 : symbol) (e2 : ExprS) (body : ExprS)]
  [letrecS (v : symbol) (e : ExprS) (body : ExprS)]
  [lambda2S   (arg1 : symbol) (arg2 : symbol) (body : ExprS)]
  [app2S   (fun : ExprS) (arg1 : ExprS) (arg2 : ExprS)]
  [quoteS  (s : symbol)]
  [equalS  (l : ExprS) (r : ExprS)]
  )

; We need a new value for the box
(define-type Value
  [numV  (n : number)]
  [closV (arg : symbol) (body : ExprC) (env : Env)]
  [consV (car : Value) (cdr : Value)]
  [clos2V (arg1 : symbol) (arg2 : symbol) (body : ExprC) (env : Env)]
  [symV  (s : symbol)]
  )

; Bindings associate symbol with Boxes
; we need this to be able to change the value of a binding, which is important
; to implement letrec.
(define-type Binding
  [bind (name : symbol) (val : (boxof Value))])

; Env remains the same, we only change the Binding
(define-type-alias Env (listof Binding))
(define mt-env empty)
(define extend-env cons)

; lookup changes its return type
(define (lookup [varName : symbol] [env : Env]) : (boxof Value)
  (cond
    [(empty? env) (error 'lookup (string-append "Variável não encontrada: " 
                                                 (symbol->string varName)))]
    [else (cond
            [(symbol=? varName (bind-name (first env)))
             (bind-val (first env))]
            [else (lookup varName (rest env))])]))

; Primitive operators
(define (num+ [l : Value] [r : Value]) : Value
  (cond
    [(and (numV? l) (numV? r))
     (numV (+ (numV-n l) (numV-n r)))]
    [else
     (error 'num+ "Um dos argumentos não é número")]))

(define (num* [l : Value] [r : Value]) : Value
  (cond
    [(and (numV? l) (numV? r))
     (numV (* (numV-n l) (numV-n r)))]
    [else
     (error 'num* "Um dos argumentos não é número")]))

(define (desugar [as : ExprS]) : ExprC
  (type-case ExprS as
    [numS    (n)        (numC n)]
    [idS     (s)        (idC s)]
    [set!S   (s e)      (set!C s (desugar e))]
    [letS    (v e body) (letC v (desugar e) (desugar body))]
    [lamS    (a b)      (lamC a (desugar b))]
    [appS    (fun arg)  (appC (desugar fun) (desugar arg))]
    [plusS   (l r)      (plusC (desugar l) (desugar r))]
    [multS   (l r)      (multC (desugar l) (desugar r))]
    [bminusS (l r)      (plusC (desugar l) (multC (numC -1) (desugar r)))]
    [uminusS (e)        (multC (numC -1) (desugar e))]
    [ifS     (c y n)    (ifC (desugar c) (desugar y) (desugar n))]
    [consS   (b1 b2)    (consC (desugar b1) (desugar b2))]
    [carS    (c)        (carC (desugar c))]
    [cdrS    (c)        (cdrC (desugar c))]
    [beginS  (e1 e2)    (beginC (desugar e1) (desugar e2))]
    [let*S (v1 e1 v2 e2 body) 
              (let*C v1 (desugar e1) v2 (desugar e2) (desugar body))]
    [letrecS (v e body)
             (letC v (numC 1)
                   (beginC (set!C v (desugar e))
                           (desugar body)))]
    [lambda2S   (a1 a2 b)  (lambda2C a1 a2 (desugar b))]
    [app2S   (f a1 a2)  (app2C (desugar f) (desugar a1) (desugar a2))]
    [quoteS  (s)        (quoteC s)]
    [equalS  (l r)      (equalC (desugar l) (desugar r))]
    ))

; Return type for the interpreter, Value

(define (interp [a : ExprC] [env : Env]) : Value
  (type-case ExprC a
    [numC (n) (numV n)]
    [idC (n)  (unbox (lookup n env))]
    [lamC (a b) (closV a b env)]
    
    [set!C (v exp) 
          (begin 
            (set-box! (lookup v env) (interp exp env))
            (unbox (lookup v env)))]
    
    [appC (f a)
          (let ((closure (interp f env))
                (argvalue (interp a env)))
            (type-case Value closure
              [closV (parameter body env)
                     (interp body (extend-env (bind parameter (box argvalue)) env))]
              [else (error 'interp "operation app aplied to non-closure")]))]
    
    [letC (v e b)
          (interp b (extend-env (bind v (box (interp e env))) env))]
    
    [plusC (l r)
           (let ((left (interp l env))
                 (right (interp r env)))
             (num+ left right))]
    
    [multC (l r)
           (let ((left (interp l env))
                 (right (interp r env)))
             (if (numV? left)
                 (if (numV? right)
                     (num* left right)
                     (error 'interp "second argument of multiplication not a number value"))
                 (error 'interp "first argument of multiplication not a number value")))]
    
    [ifC (c s n) 
         (type-case Value (interp c env)
           [numV (value)
                 (if (zero? value)
                     (interp n env)
                     (interp s env))]
           [else (error 'interp "condition not a number")])]
    
    [consC (b1 b2) 
           (let ((car (interp b1 env))
                 (cdr (interp b2 env)))
             (consV car cdr))]
    
    [carC (c) 
          (type-case Value (interp c env)
            [consV (car cdr) car]
            [else (error 'interp "car applied to non-cell")])]
    
    [cdrC (c) 
          (type-case Value (interp c env)
            [consV (car cdr) cdr]
            [else (error 'interp "cdr applied to non-cell")])]
    
    ;; executa e1, depois e2, retorna valor de e2
    [beginC (e1 e2)
            (begin
              (interp e1 env)
              (interp e2 env))]
    
    ;; let*
    [let*C (v1 e1 v2 e2 body)
           (let ((val1 (interp e1 env)))
             (interp body (extend-env (bind v1 (box val1))
                            (extend-env (bind v2 (box (interp e2 (extend-env (bind v1 (box val1)) env)))) env))))]
    
    ;; lambda2 e call2
    [lambda2C (a1 a2 b) (clos2V a1 a2 b env)]
    
    [app2C (f a1 a2)
           (let ((closure (interp f env))
                 (arg1val (interp a1 env))
                 (arg2val (interp a2 env)))
             (type-case Value closure
               [clos2V (param1 param2 body clos-env)
                 (interp body 
                   (extend-env (bind param1 (box arg1val))
                     (extend-env (bind param2 (box arg2val)) 
                       clos-env)))]
               [else (error 'interp "call2 application applied to non-closure")]))]
    
    ;; quote
    [quoteC (s) (symV s)]
    
    ;; equal
    [equalC (l r)
            (let ((left (interp l env))
                  (right (interp r env)))
              (type-case Value left
                [numV (lval)
                      (type-case Value right
                        [numV (rval)
                              (if (= lval rval)
                                  (numV 1)
                                  (numV 0))]
                        [else (error 'interp "second argument of equality not a number")])]
                [else (error 'interp "first argument of equality not a number")]))]
    ))

; Parser with funny instructions for boxes
(define (parse [s : s-expression]) : ExprS
  (cond
    [(s-exp-number? s) (numS (s-exp->number s))]
    [(s-exp-symbol? s) (idS (s-exp->symbol s))]
    [(s-exp-list? s)
     (let ([sl (s-exp->list s)])
       (case (s-exp->symbol (first sl))
         [(+) (plusS (parse (second sl)) (parse (third sl)))]
         [(*) (multS (parse (second sl)) (parse (third sl)))]
         [(-) (bminusS (parse (second sl)) (parse (third sl)))]
         [(~) (uminusS (parse (second sl)))]
         [(let) (letS (s-exp->symbol (second sl)) (parse (third sl)) (parse (fourth sl)))]
         [(set!) (set!S (s-exp->symbol (second sl)) (parse (third sl)))]
         [(=) (equalS (parse (second sl)) (parse (third sl)))]
         [(lambda) (lamS (s-exp->symbol (second sl)) (parse (third sl)))]
         [(call) (appS (parse (second sl)) (parse (third sl)))]
         [(if) (ifS (parse (second sl)) (parse (third sl)) (parse (fourth sl)))]
         [(cons) (consS (parse (second sl)) (parse (third sl)))]
         [(car) (carS (parse (second sl)))]
         [(cdr) (cdrS (parse (second sl)))]
         [(begin) (beginS (parse (second sl)) (parse (third sl)))]
         [(let*) (let*S (s-exp->symbol (second sl)) (parse (third sl))
                          (s-exp->symbol (fourth sl)) (parse (list-ref sl 4))
                          (parse (list-ref sl 5)))]
         [(letrec) (letrecS (s-exp->symbol (second sl)) (parse (third sl)) 
                            (parse (fourth sl)))]
         [(lambda2) (lambda2S (s-exp->symbol (second sl)) (s-exp->symbol (third sl))
                           (parse (fourth sl)))]
         [(call2) (app2S (parse (second sl)) (parse (third sl)) (parse (fourth sl)))]
         [(quote) (quoteS (s-exp->symbol (second sl)))]
         [else (error 'parse "invalid list input")]))]
    [else (error 'parse "invalid list input")]))

; Facilitator
(define (interpS [s : s-expression]) (interp (desugar (parse s)) mt-env))

; Readloop

(define (readloop) : void
  (let ((s (read)))
    (cond
      [(s-exp-list? s)
       (let* ((sl (s-exp->list s))
              (operator (s-exp->symbol (first sl))))
         (case operator
           [(@END) (void)]
           [else
            (let* ((arits (parse s))
                   (aritc (desugar arits))
                   (value (interpS s)))
              (begin
                (display arits)
                (display "\n")
                (display aritc)
                (display "\n")
                (display value)
                (display "\n")
                (readloop)))]))]
      [else (error 'parse "invalid input")])))

(readloop)

;; ============================================================================
;; TESTES
;; ============================================================================

; (test (interp (carC (consC (numC 10) (numC 20))) mt-env) (numV 10))
; (test (interpS '(begin (+ 1 2) (+ 3 4))) (numV 7))
; (test (interpS '(let* x 5 y (+ x 3) (+ y x))) (numV 13))
; (test (interpS '(letrec fact (lambda n 
;                                (if n 
;                                    (* n (call fact (- n 1))) 
;                                    1))
;                         (call fact 5)))
;       (numV 120))
; (test (interpS '(call2 (lambda2 x y (+ x y)) 10 20)) (numV 30))
; (test (interpS '(quote alan)) (symV 'alan))

; (interpS '(+ 10 (call (lambda x (car x)) (cons 15 16))))
; (interpS '(call (lambda x (+ x 5)) 8))
; (interpS '(call (lambda f (call f (~ 32))) (lambda x (- 200 x))))