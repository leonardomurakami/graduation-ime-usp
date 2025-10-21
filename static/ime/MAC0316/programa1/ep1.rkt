#lang plai-typed

#|
 | EP1 - MAC0316
 |#

;; ============================================================================
;; TIPOS DE DADOS
;; ============================================================================

(define-type ExprC
  [numC    (n : number)]
  [idC     (s : symbol)]
  [setC    (s : symbol) (e : ExprC)]
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
  [letStarC (v1 : symbol) (e1 : ExprC)
            (v2 : symbol) (e2 : ExprC) (body : ExprC)]
  [lam2C   (arg1 : symbol) (arg2 : symbol) (body : ExprC)]
  [app2C   (fun : ExprC) (arg1 : ExprC) (arg2 : ExprC)]
  [quoteC  (s : symbol)]
  [readLoopC]
  )

(define-type ExprS
  [numS    (n : number)]
  [idS     (s : symbol)]
  [setS    (s : symbol) (v : ExprS)]
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
  [letStarS (v1 : symbol) (e1 : ExprS) 
            (v2 : symbol) (e2 : ExprS) (body : ExprS)]
  [letrecS (v : symbol) (e : ExprS) (body : ExprS)]
  [lam2S   (arg1 : symbol) (arg2 : symbol) (body : ExprS)]
  [app2S   (fun : ExprS) (arg1 : ExprS) (arg2 : ExprS)]
  [quoteS  (s : symbol)]
  [readLoopS]
  )

(define-type Value
  [numV  (n : number)]
  [closV (arg : symbol) (body : ExprC) (env : Env)]
  [consV (car : Value) (cdr : Value)]
  [clos2V (arg1 : symbol) (arg2 : symbol) (body : ExprC) (env : Env)]
  [symV  (s : symbol)]
  )

(define-type Binding
  [bind (name : symbol) (val : (boxof Value))])

(define-type-alias Env (listof Binding))
(define mt-env empty)
(define extend-env cons)

;; ============================================================================
;; FUNÇÕES AUXILIARES
;; ============================================================================

(define (lookup [varName : symbol] [env : Env]) : (boxof Value)
  (cond
    [(empty? env) (error 'lookup (string-append "Variável não encontrada: " 
                                                 (symbol->string varName)))]
    [else (cond
            [(symbol=? varName (bind-name (first env)))
             (bind-val (first env))]
            [else (lookup varName (rest env))])]))

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

;; ============================================================================
;; DESUGAR
;; ============================================================================

(define (desugar [as : ExprS]) : ExprC
  (type-case ExprS as
    [numS    (n)        (numC n)]
    [idS     (s)        (idC s)]
    [setS    (s e)      (setC s (desugar e))]
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
    [letStarS (v1 e1 v2 e2 body) 
              (letStarC v1 (desugar e1) v2 (desugar e2) (desugar body))]
    [letrecS (v e body)
             (letC v (numC 0)
                   (beginC (setC v (desugar e))
                           (desugar body)))]
    [lam2S   (a1 a2 b)  (lam2C a1 a2 (desugar b))]
    [app2S   (f a1 a2)  (app2C (desugar f) (desugar a1) (desugar a2))]
    [quoteS  (s)        (quoteC s)]
    [readLoopS ()       (readLoopC)]
    ))

;; ============================================================================
;; INTERPRETADOR
;; ============================================================================

(define (interp [a : ExprC] [env : Env]) : Value
  (type-case ExprC a
    [numC (n) (numV n)]
    [idC (n)  (unbox (lookup n env))]
    [lamC (a b) (closV a b env)]
    
    [setC (v exp) 
          (begin 
            (set-box! (lookup v env) (interp exp env))
            (unbox (lookup v env)))]
    
    [appC (f a)
          (let ((closure (interp f env))
                (argvalue (interp a env)))
            (type-case Value closure
              [closV (parameter body env)
                     (interp body (extend-env (bind parameter (box argvalue)) env))]
              [else (error 'interp "Aplicação a não-closure")]))]
    
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
                     (error 'interp "Segundo argumento de * não é número"))
                 (error 'interp "Primeiro argumento de * não é número")))]
    
    [ifC (c s n) 
         (type-case Value (interp c env)
           [numV (value)
                 (if (zero? value)
                     (interp n env)
                     (interp s env))]
           [else (error 'interp "Condição não é número")])]
    
    [consC (b1 b2) 
           (let ((car (interp b1 env))
                 (cdr (interp b2 env)))
             (consV car cdr))]
    
    [carC (c) 
          (type-case Value (interp c env)
            [consV (car cdr) car]
            [else (error 'interp "car aplicado a não-célula")])]
    
    [cdrC (c) 
          (type-case Value (interp c env)
            [consV (car cdr) cdr]
            [else (error 'interp "cdr aplicado a não-célula")])]
    
    ;; executa e1, depois e2, retorna valor de e2
    [beginC (e1 e2)
            (begin
              (interp e1 env)
              (interp e2 env))]
    
    ;; let* v1=e1 v2=e2 in body => let v1=e1 in (let v2=e2 in body)
    [letStarC (v1 e1 v2 e2 body)
              (let ((val1 (interp e1 env)))
                (let ((env2 (extend-env (bind v1 (box val1)) env)))
                  (let ((val2 (interp e2 env2)))
                    (interp body (extend-env (bind v2 (box val2)) env2)))))]
    
    ;; lambda2 e call2
    [lam2C (a1 a2 b) (clos2V a1 a2 b env)]
    
    [app2C (f a1 a2)
           (let ((closure (interp f env))
                 (arg1val (interp a1 env))
                 (arg2val (interp a2 env)))
             (type-case Value closure
               [clos2V (param1 param2 body env)
                       (interp body 
                               (extend-env (bind param1 (box arg1val))
                                          (extend-env (bind param2 (box arg2val)) 
                                                     env)))]
               [else (error 'interp "Aplicação call2 a não-closure de 2 parâmetros")]))]
    
    ;; quote
    [quoteC (s) (symV s)]
    
    ;; read-loop
    [readLoopC () 
               (begin
                 (read-and-eval-loop env)
                 (symV 'finished))]
    ))

;; ============================================================================
;; READ-LOOP
;; ============================================================================

(define (read-and-eval-loop [env : Env]) : void
  (let ((input (read)))
    (if (and (s-exp-symbol? input) (eq? (s-exp->symbol input) '@end))
        (display "FINISHED-INTERPRETER\n")
        (begin
          (display "\ninterpret-command: ")
          (display input)
          (display "\nresult: ")
          (display (interp (desugar (parse input)) env))
          (display "\n")
          (read-and-eval-loop env)))))

;; ============================================================================
;; PARSER
;; ============================================================================

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
         [(set!) (setS (s-exp->symbol (second sl)) (parse (third sl)))]
         [(lambda) (lamS (s-exp->symbol (second sl)) (parse (third sl)))]
         [(call) (appS (parse (second sl)) (parse (third sl)))]
         [(if) (ifS (parse (second sl)) (parse (third sl)) (parse (fourth sl)))]
         [(cons) (consS (parse (second sl)) (parse (third sl)))]
         [(car) (carS (parse (second sl)))]
         [(cdr) (cdrS (parse (second sl)))]
         ;; Novos para EP1
         [(begin) (beginS (parse (second sl)) (parse (third sl)))]
         [(let*) (letStarS (s-exp->symbol (second sl)) (parse (third sl))
                          (s-exp->symbol (fourth sl)) (parse (list-ref sl 4))
                          (parse (list-ref sl 5)))]
         [(letrec) (letrecS (s-exp->symbol (second sl)) (parse (third sl)) 
                           (parse (fourth sl)))]
         [(lambda2) (lam2S (s-exp->symbol (second sl)) (s-exp->symbol (third sl))
                          (parse (fourth sl)))]
         [(call2) (app2S (parse (second sl)) (parse (third sl)) (parse (fourth sl)))]
         [(quote) (quoteS (s-exp->symbol (second sl)))]
         [(read-loop) (readLoopS)]
         [else (error 'parse "Entrada de lista inválida")]))]
    [else (error 'parse "Entrada inválida")]))

;; ============================================================================
;; FACILITADOR
;; ============================================================================

(define (interpS [s : s-expression]) (interp (desugar (parse s)) mt-env))

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
; (interpS '(read-loop))