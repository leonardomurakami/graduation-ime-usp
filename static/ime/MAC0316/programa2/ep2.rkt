#lang plai-typed
; este interpretador aumenta o closureTyped para incluir
; cons, car, cdr, valor nulo (descrito como  ())
; e display
; display imprime o valor passado seguido de um ";". Nao mudamos de linha 

; Basic expressions
(define-type ExprC
  [numC  (n : number)]
  [idC   (s : symbol)]
  [plusC (l : ExprC) (r : ExprC)]
  [multC (l : ExprC) (r : ExprC)]
  [equalC (l : ExprC) (r : ExprC)]
  [lamC  (arg : symbol) (body : ExprC)]
  [appC  (fun : ExprC) (arg : ExprC)]
  [ifC   (c : ExprC) (y : ExprC) (n : ExprC)]
  [seqC  (e1 : ExprC) (e2 : ExprC)]
  [letC  (name : symbol) (arg : ExprC) (body : ExprC)]
  [consC (car : ExprC) (cdr : ExprC)]
  [carC  (cell : ExprC)]
  [cdrC (cell : ExprC)]
  [displayC (exp : ExprC)]
  [quoteC  (sym : symbol)]
  [nullC  ]
  )


; Sugared expressions
(define-type ExprS
  [numS    (n : number)]
  [idS     (s : symbol)]
  [lamS    (arg : symbol) (body : ExprS)]
  [appS    (fun : ExprS) (arg : ExprS)]
  [plusS   (l : ExprS) (r : ExprS)]
  [bminusS (l : ExprS) (r : ExprS)]
  [equalS  (l : ExprS) (r : ExprS)]
  [uminusS (e : ExprS)]
  [multS   (l : ExprS) (r : ExprS)]
  [ifS     (c : ExprS) (y : ExprS) (n : ExprS)]
  [seqS    (e1 : ExprS) (e2 : ExprS)]
  [letS    (name : symbol) (arg : ExprS) (body : ExprS)]
  [consS (car : ExprS) (cdr : ExprS)]
  [carS (cell : ExprS)]
  [cdrS (cell : ExprS)]
  [displayS (exp : ExprS)]
  [quoteS  (sym : symbol)]
  [nullS ]
 )


; Removing the sugar
(define (desugar [as : ExprS]) : ExprC
  (type-case ExprS as
    [numS    (n)        (numC n)]
    [idS     (s)        (idC s)]
    [lamS    (a b)      (lamC a (desugar b))]
    [appS    (fun arg)  (appC (desugar fun) (desugar arg))]
    [plusS   (l r)      (plusC (desugar l) (desugar r))]
    [multS   (l r)      (multC (desugar l) (desugar r))]
    [equalS  (l r)      (equalC (desugar l) (desugar r))]
    [bminusS (l r)      (plusC (desugar l) (multC (numC -1) (desugar r)))]
    [uminusS (e)        (multC (numC -1) (desugar e))]
    [ifS     (c s n)    (ifC (desugar c) (desugar s) (desugar n))]
    [seqS    (e1 e2)    (seqC (desugar e1) (desugar e2))]
    [letS    (n a b)    (letC n (desugar a) (desugar b))]
    [consS   (car cdr) (consC (desugar car) (desugar cdr))]
    [carS    (exp)     (carC (desugar  exp))]
    [cdrS    (exp)     (cdrC (desugar  exp))]
    [displayS (exp)    (displayC (desugar exp))]
    [quoteS (sym) (quoteC sym)]
    [nullS  () (nullC)]
    ))

; We need a new value for the box
(define-type Value
  [numV  (n : number)]
  [nullV ]
  [quoteV (symb : symbol)]
  [closV (arg : symbol) (body : ExprC) (env : Env)]
  [cellV (first : (boxof Value)) (second : (boxof Value))]
  [suspensionV (body : ExprC) (env : Env)]
  )


; Bindings associate symbol with location
(define-type Binding
        [bind (name : symbol) (val : (boxof Value))])

; Env remains the same, we only change the Binding
(define-type-alias Env (listof Binding))
(define mt-env empty)
(define extend-env cons)


; Find the name of a variable
(define (lookup [for : symbol] [env : Env]) : (boxof Value)
       (cond
            [(empty? env) (error 'lookup (string-append (symbol->string for) " was not found"))] ; variable is undefined
            [else (cond
                  [(symbol=? for (bind-name (first env)))   ; found it!
                                 (bind-val (first env))]
                  [else (lookup for (rest env))])]))        ; check in the rest


; Auxiliary operators
(define (num+ [l : Value] [r : Value]) : Value
    (cond
        [(and (numV? l) (numV? r))
             (numV (+ (numV-n l) (numV-n r)))]
        [else
             (error 'num+ "One of the arguments is not a number")]))

(define (num* [l : Value] [r : Value]) : Value
    (cond
        [(and (numV? l) (numV? r))
             (numV (* (numV-n l) (numV-n r)))]
        [else
             (error 'num* "One of the arguments is not a number")]))

(define (valueEq [l : Value] [r : Value]) : Value
    (if (equal? l r)
        (numV 1)
        (numV 0)))

;IMPORTANTE -- FUNCAO AUXILIAR EM BOX PARA ELIMINAR SUSPENSOES
;esta função é essencial para garantir que as suspensões, uma vez avaiadas,
;são subsituidas pelo valor resultante. Você agora, quando criar variáveis em ambientes, ou
;quando criar células, colocar um box com uma suspensionV contendo a expressão a ser avaliada e o
;ambiente
;ao acessar variáveis no ambiente (idC)  e nos campos de uma célula (carC e cdrC), você deve usar
;olha-valor-box

(define(olha-valor-box  [box :(boxof Value)] )
  (let ((box-content (unbox box)))
    (type-case Value box-content
      [suspensionV (exp env)
                   (let ((new-content (interp exp env)))
                     (begin(set-box! box new-content)
                           (unbox box)))]
      [else box-content])))
   
; Interpreter
(define (interp [a : ExprC] [env : Env]) : Value
  (type-case ExprC a
    ; Numbers just evaluta to their equivalent Value
    [numC (n) (numV n)]

    ; IDs are retrieved from the Env and unboxed
    [idC (n) (olha-valor-box (lookup n env))]

    ; Lambdas evaluate to closures, which save the environment
    [lamC (a b) (closV a b env)]

    ; Application of function
    [appC (f a)
          (let ([f-value (interp f env)])
            (interp (closV-body f-value)
                    (extend-env
                        (bind (closV-arg f-value) (box (suspensionV a env)))
                        (closV-env f-value))))]

    ; Sum two numbers using auxiliary function
    [plusC (l r) (num+ (interp l env) (interp r env))]

    ; Multiplies two numbers using auxiliary function
    [multC (l r) (num* (interp l env) (interp r env))]
    ; compares two numbers using auxiliary function
    [equalC (l r) (valueEq (interp l env) (interp r env))]

    ; Conditional operator
    [ifC (c s n) (if (zero? (numV-n (interp c env))) (interp n env) (interp s env))]

    ; Sequence of operations
    [seqC (b1 b2) (begin (interp b1 env) (interp b2 env))] ; usaremos o begin para forçar a avaliação
                                                           ; de algo no primeiro comando para ver no segundo

    ; Declaration of variable
    [letC (name arg body)
          (let* ([new-bind (bind name (box (suspensionV arg env)))]
                 [new-env (extend-env new-bind env)])
            (interp body new-env))]
    ; Cell operations
    [consC (car cdr)
           (cellV (box (suspensionV car env))
                  (box (suspensionV cdr env)))]
    [carC  (exp) (olha-valor-box (cellV-first (interp exp env)))]
    [cdrC  (exp) (olha-valor-box (cellV-second (interp exp env)))]
    ;Display values
    [displayC (exp) (let ((value (interp exp env)))
                      (begin (print-value value)
                             (display ";")
                             value))]
    [quoteC (sym) (quoteV sym)]
    [nullC () (nullV)]))

(define (parse [s : s-expression]) : ExprS
  (cond
    [(s-exp-number? s) (numS (s-exp->number s))]
    [(s-exp-symbol? s) (idS (s-exp->symbol s))]
    [(s-exp-list? s)
     (let ([sl (s-exp->list s)])
       (if (empty? sl)
           (nullS)
           (case (s-exp->symbol (first sl))
             [(+) (plusS (parse (second sl)) (parse (third sl)))]
             [(-) (bminusS (parse (second sl)) (parse (third sl)))]
             [(*) (multS (parse (second sl)) (parse (third sl)))]
             [(~) (uminusS (parse (second sl)))]
             [(=) (equalS (parse (second sl)) (parse (third sl)))]
             [(lambda) (lamS (s-exp->symbol (second sl)) (parse (third sl)))]
             [(call) (appS (parse (second sl)) (parse (third sl)))]
             [(if) (ifS (parse (second sl)) (parse (third sl)) (parse (fourth sl)))]
             [(seq) (seqS (parse (second sl)) (parse (third sl)))]
             [(let) (letS (s-exp->symbol (second sl))
                          (parse (third sl))
                          (parse (fourth sl)))]
             [(cons) (consS (parse (second sl)) (parse (third sl)))]
             [(car) (carS (parse (second sl)))]
             [(cdr) (cdrS (parse (second sl)))]
             [(display) (displayS (parse (second sl)))]
             [(quote) (quoteS (s-exp->symbol (second sl)))]
             [else (error 'parse "invalid list input")])))]
    [else (error 'parse "invalid input")]))

(define (interpS [s : s-expression]) : Value
  (interp (desugar (parse s)) mt-env))

; Print-value : imprime valores, listas e suspensões. Assim vocês
; podem usar display para ver quando temos suspensões e quando
; temos valores nas células e variáveis
(define (print-value [value : Value])
  (type-case Value value
                        [numV   (n) (display n)]
                        [quoteV (s)
                                (begin (display "(quote ")
                                       (display s)
                                       (display ")"))]
                        [closV (arg body env)
                               (begin (display "<<")
                                      (print-exp body)
                                      (display ";")
                                      (print-environment env)
                                      (display ">>"))]
                        [suspensionV (body env)
                               (begin (display "<|")
                                      (print-exp body)
                                      (display ";")
                                      (print-environment env)
                                      (display "|>"))]
                       
                        [cellV (first second)
                               (begin (display "(")
                                      (print-list value); pequeno truque, nao olho os valores, imprimo a lista 
                                      (display ")"))]
                        [nullV ()
                               (display '())]))
;para imprimir uma lista toda
; Print-list-cell: imprime uma lista completa
(define (print-list cell) : void
  (begin 
         (print-value (unbox (cellV-first cell)))
         (display " ")
         (let ([rest (unbox (cellV-second cell))])
           (type-case Value rest 
             [nullV () (display "")] ; null at the end of the list is not printed
             [cellV (first second) (print-list rest)]
             [else (begin (display ".")
                        (print-value rest))]))))  ; quando cdr não aponta para outra célula

; Print-exp: imprime expressões (usada para imprimir closures e
; suspensões)
(define (print-exp [exp : ExprC]) : void
  (type-case ExprC exp
    [plusC (a b) (begin (display "(")
                        (display "+ ")
                        (print-exp a)
                        (display " ")
                        (print-exp b)
                        (display ")"))]
    [multC (a b) (begin (display "(")
                        (display "* ")
                        (print-exp a)
                        (display " ")
                        (print-exp b)
                        (display ")"))]
    [equalC (a b) (begin (display "(")
                        (display "= ")
                        (print-exp a)
                        (display " ")
                        (print-exp b)
                        (display ")"))]
    
    [lamC (param body) (begin (display "(")
                        (display "lambda ")
                        (display param)
                        (display " ")
                        (print-exp body)
                        (display ")"))]
    [numC  (n) (display n)]
    [idC   (id)(display id)]
    [appC  (fun arg) (begin (display "(")
                            (print-exp fun)
                            (display " ")
                            (print-exp arg)
                            (display ")"))]
    [ifC   (c y n)
           (begin (display "(if ")
                  (print-exp c)
                  (display " ")
                  (print-exp y)
                  (display " ")
                  (print-exp n)
                  (display ")"))]
    [seqC  (e1 e2 )
                      (begin (display "(seq ")
                             (print-exp e1)
                             (display " ")
                             (print-exp e2)
                             (display ")"))]
    
    [letC  (name arg body) 
           (begin (display "(let (( ")
                  (display name)
                  (display " ")
                  (print-exp arg)
                  (display "))")
                  (print-exp body))]
    [consC (car cdr)
           (begin (display "(cons ")
                  (print-exp car)
                  (display " ")
                  (print-exp cdr)
                  (display ")"))]
    [carC  (cell)
          (begin (display "(car ")
                  (print-exp cell)
                  (display ")"))]
    [cdrC  (cell)
           (begin (display "(cdr ")
                  (print-exp cell)
                  (display ")"))]
    [displayC  (expr)
               (begin (display "(display ")
                      (print-exp expr)
                      (display ")"))]
    
    [quoteC  (sym)
             (begin (display "(quote ")
                      (display sym)
                      (display ")"))]
    [nullC  () (display "()")]
  ))

(define (print-environment [environment : Env])
  (begin 
    (display "{")
    (print-binding-list environment)
    (display "}")
  )
  )
(define (print-binding-list binding-list)
  (if (empty? binding-list)
      (display ""); nothing to be printed
      (begin 
        (display (bind-name (first binding-list)))
        (display "->")
        (print-value (unbox (bind-val (first binding-list))))
        (display ";")
        (print-binding-list (rest binding-list))
        )
      )
  )

;READLOOP para rodar testes
(define (readloop ) : void
  (let((s (read)))
    (cond
      [(s-exp-list? s) (let* ((sl (s-exp->list s))
                              (operator (s-exp->symbol (first sl))))
                         (case operator
                           [(@END) (void)]
                           [else  (let* ( (arits (parse s))
                                           (aritc (desugar arits))
                                           (value (interpS s)))
                                     (begin (display arits)
                                            (display "\n")
                                            (display aritc)
                                            (display "\n")
                                            (display value)
                                            (display "\n")
                                            (readloop)))]))]            
      [else (error 'parse "invalid input")])))
(readloop)

; (interpS '(= 5 5))
; (interpS '(= 3 7))
; (interpS '(= (quote abc) (quote abc)))
; (interpS '(= (quote x) (quote y)))
; (interpS '(= () ()))
; (interpS '(let x (+ 10 20)
;               (+ x x)))
; (interpS '(let lst (cons (+ 1 2) (cons (+ 3 4) ()))
;               (car lst)))
; (interpS '(let lst (cons 1 (cons 2 (cons 3 ())))
;               (car (cdr lst))))
; (interpS '(display (cons 1 (cons 2 (cons 3 ())))))
; (interpS '(display (cons 1 (cons (quote a) (cons 5 6)))))
; (interpS '(car (cons 10 (cons 20 ()))))
; (interpS '(cdr (cons 10 (cons 20 ()))))
; (interpS '(display (lambda x (+ x 2))))
; (interpS '(display (call (lambda y (lambda x (+ x y))) 5)))
; (interpS '(call (call (lambda y (lambda x (+ x y))) 5) 3))
; (interpS '(let expensive (seq (display 999) (+ 50 50))
;               (let lst (cons expensive (cons expensive ()))
;                    (+ (car lst) (car (cdr lst))))))
; (interpS '(let lst (cons (+ 10 20) (cons (+ 30 40) ()))
;               (+ (car lst) (car (cdr lst)))))
; (interpS '(let x (seq (display 777) 42)
;               (* x x)))
; (interpS '(if (= 3 3) 100 200))
; (interpS '(if (= (quote yes) (quote yes)) 
;              (quote correct)
;              (quote wrong)))
; (interpS '(let a (+ 1 2)
;               (let b (+ a 3)
;                    (+ a b))))
; (interpS '(let f (lambda x (+ x 1))
;               (display (cons f (cons f ())))))
; (interpS '(display (cons (lambda x (* x 5)) ())))