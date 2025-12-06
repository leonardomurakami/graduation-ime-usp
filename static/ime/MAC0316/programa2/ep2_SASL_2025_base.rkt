#lang plai-typed
; este interpretador aumenta o closureTyped para incluir
; cons, car, cdr, valor nulo (descrito como  ())
; e display
; display imprime o valor passado seguido de um ";". Nao mudamos de linha 

; Basic expressions
(define-type ExprC
  [numC  (n : number)]
  ;[idC   (s : symbol)] ;removido esperando implementacao de av. por demanda
  [plusC (l : ExprC) (r : ExprC)]
  [multC (l : ExprC) (r : ExprC)]
  [equalC (l : ExprC) (r : ExprC)]
  [lamC  (arg : symbol) (body : ExprC)]
  ;[appC  (fun : ExprC) (arg : ExprC)] ;removido esperando implementacao de av. por demanda
  [ifC   (c : ExprC) (y : ExprC) (n : ExprC)]
  [seqC  (e1 : ExprC) (e2 : ExprC)]
  ;[setC  (var : symbol) (arg : ExprC)] ; removido, tiramos os efeitos colaterais
  ;[letC  (name : symbol) (arg : ExprC) (body : ExprC)] ;removido esperando implementacao de av. por demanda
  ;[consC (car : ExprC) (cdr : ExprC)];removido esperando implementacao de av. por demanda
  ;[carC  (cell : ExprC) ];removido esperando implementacao de av. por demanda
  ;[cdrC (cell : ExprC)];removido esperando implementacao de av. por demanda
  [displayC (exp : ExprC)]
  [quoteC  (sym : symbol)]
  [nullC  ]
  )


; Sugared expressions
(define-type ExprS
  [numS    (n : number)]
  ;[idS     (s : symbol)] ;removido esperando implementacao de av. por demanda
  [lamS    (arg : symbol) (body : ExprS)]
  ;[appS    (fun : ExprS) (arg : ExprS)] ;removido esperando implementacao de av. por demanda
  [plusS   (l : ExprS) (r : ExprS)]
  [bminusS (l : ExprS) (r : ExprS)]
  [equalS  (l : ExprS) (r : ExprS)]
  [uminusS (e : ExprS)]
  [multS   (l : ExprS) (r : ExprS)]
  [ifS     (c : ExprS) (y : ExprS) (n : ExprS)]
  [seqS    (e1 : ExprS) (e2 : ExprS)]
  ; [setS    (var : symbol) (arg : ExprS)];retirado na avaliação por demanda
  ;[letS    (name : symbol) (arg : ExprS) (body : ExprS)];removido esperando implementacao de av. por demanda
  ;[consS (car : ExprS) (cdr : ExprS)] ;removido esperando implementacao de av. por demanda
  ;[carS (cell : ExprS) ];removido esperando implementacao de av. por demanda
  ;[cdrS (cell : ExprS)];removido esperando implementacao de av. por demanda
  [displayS (exp : ExprS)]
  [quoteS  (sym : symbol)]
  [nullS ]
 )


; Removing the sugar
(define (desugar [as : ExprS]) : ExprC
  (type-case ExprS as
    [numS    (n)        (numC n)]
    ;[idS     (s)        (idC s)];removido esperando implementacao de av. por demanda
    [lamS    (a b)      (lamC a (desugar b))]
    ;[appS    (fun arg)  (appC (desugar fun) (desugar arg))];removido esperando implementacao de av. por demanda
    [plusS   (l r)      (plusC (desugar l) (desugar r))]
    [multS   (l r)      (multC (desugar l) (desugar r))]
    [equalS  (l r)      (equalC (desugar l) (desugar r))]
    [bminusS (l r)      (plusC (desugar l) (multC (numC -1) (desugar r)))]
    [uminusS (e)        (multC (numC -1) (desugar e))]
    [ifS     (c s n)    (ifC (desugar c) (desugar s) (desugar n))]
    [seqS    (e1 e2)    (seqC (desugar e1) (desugar e2))]
    ;[setS    (var expr) (setC  var (desugar expr))] ;removido esperando implementacao de av. por demanda
    ;[letS    (n a b)    (letC n (desugar a) (desugar b))];removido esperando implementacao de av. por demanda
    ;[consS   (car cdr) (consC (desugar car) (desugar cdr))];removido esperando implementacao de av. por demanda
    ;[carS    (exp)     (carC (desugar  exp)) ];removido esperando implementacao de av. por demanda
    ;[cdrS    (exp)     (cdrC (desugar  exp)) ];removido esperando implementacao de av. por demanda
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
  ;vc deve fazer nova implementação de cellV usando boxes
  ;[cellV (first :...) (second : ...)]
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
;nova versão, você agora deve usar o equal? do plai-typed para comparar numeros e symbolos
;para isso vai precisar ver o tipo de cada argumento e extrair o conteúdo
(define (valueEq [l : Value] [r : Value]) : Value
    (let ((value1 '() ); troque pela extracao do valor
                   
          (value2 '())) ;troque pela extracao do valor
      (if (equal? value1 value2)
          (numV 1)
          (numV 0))))
 
; Interpreter
(define (interp [a : ExprC] [env : Env]) : Value
  (type-case ExprC a
    ; Numbers just evaluta to their equivalent Value
    [numC (n) (numV n)]

    ; IDs are retrieved from the Env and unboxed
    ;lembre-se que agora você precisa ter certeza que enventuais suspensões são calculadas e subsituidas
    ;código antigo abaixo
    ;[idC (n) (unbox (lookup n env))]

    ; Lambdas evaluate to closures, which save the environment
    [lamC (a b) (closV a b env)]

    ; Application of function
    ; aqui você deve lembrar que, na extensão do ambiente, deve colcoar uma suspensão associada à variável
    ;abaixo o código antigo
    ;[appC (f a)
    ;      (let ([f-value (interp f env)])
    ;        (interp (closV-body f-value)
    ;                (extend-env
    ;                    (bind (closV-arg f-value) (interp a env)))
    ;                    (closV-env f-value)
    ;                )))]

    ; Sum two numbers using auxiliary function
    [plusC (l r) (num+ (interp l env) (interp r env))]

    ; Multiplies two numbers using auxiliary function
    [multC (l r) (num* (interp l env) (interp r env))]
    ; compares two numbers using auxiliary function
    [equalC (l r) (valueEq (interp l env) (interp r env))];vc vai precisar completar implementacao de valueEqual

    ; Conditional operator
    [ifC (c s n) (if (zero? (numV-n (interp c env))) (interp n env) (interp s env))]

    ; Sequence of operations
    [seqC (b1 b2) (begin (interp b1 env) (interp b2 env))] ; usaremos o begin para forçar a avaliação
                                                           ; de algo no primeiro comando para ver no segundo

    ; Attribution of variables eliminado! não queremos efeitos colaterais
    ;[setC (var val) (let ([b (lookup var env)])
    ;                  (begin (set-box! b (interp val env)) (unbox b)))]

    ; Declaration of variable
    ;aqui, como a aplicacao de funçoes, precisamos suspender o corpo da avaliacao
    ;abaixo a versão antiga
    ;[letC (name arg body)
    ;      (let* ([new-bind (bind name (box (interp arg env)))]
    ;             [new-env (extend-env new-bind env)])
    ;        (interp body new-env))]
    ; Cell operations
    ;aqui você deve tambem garantir que argumentos do car são suspensos, colocando a suspensão
    ;dentro de um box
    ;avaliação de car e cdr deve trocar a suspensão pelo valor
    ;novamente, temos aqui a versão antiga
    ;[consC (car cdr)
    ;       (cellV (interp car env))
    ;              (interp cdr env)))]
    ;[carC  (exp) (cellV-first (interp exp env))]
    ;[cdrC  (exp) (cellV-second (interp exp env))]
    ;Display values
    [displayC (exp) (let ((value (interp exp env)))
                      (begin (print-value value)
                             (display "\n") ; one value per line in our version of display
                             value))]
    ;Symbol
    [quoteC (sym) (quoteV sym)]
    ;Null
    [nullC  () (nullV)]
    
    ))


; Parser
(define (parse [s : s-expression]) : ExprS
  (cond
    [(s-exp-number? s) (numS (s-exp->number s))]
    ;[(s-exp-symbol? s) (idS (s-exp->symbol s))]; removido até implementação de av. por demanda
    [(s-exp-list? s)
     (let ([sl (s-exp->list s)])
       (if (empty? sl)
           (nullS)
           (case (s-exp->symbol (first sl))
             [(+) (plusS (parse (second sl)) (parse (third sl)))]
             [(*) (multS (parse (second sl)) (parse (third sl)))]
             [(-) (bminusS (parse (second sl)) (parse (third sl)))]
             [(=) (equalS (parse (second sl) ) (parse (third sl)))]
             [(~) (uminusS (parse (second sl)))]
             [(lambda) (lamS (s-exp->symbol (second sl)) (parse (third sl)))] ; definição
             ;[(call) (appS (parse (second sl)) (parse (third sl)))];removido esperando implementacao de av. por demanda
             [(if) (ifS (parse (second sl)) (parse (third sl)) (parse (fourth sl)))]
             [(begin) (seqS (parse (second sl)) (parse (third sl)))]
             ;[(set!) (setS (s-exp->symbol (second sl)) (parse (third sl)))];eliminado
             ;[(let) (letS (s-exp->symbol (second sl))
             ;             (parse (third  sl))
             ;             (parse (fourth sl)))];removido esperando implementacao de av. por demanda
             ;[(cons) (consS (parse (second sl)) (parse (third sl)))];removido esperando implementacao de av. por demanda
             ;[(car) (carS (parse (second sl)))];removido esperando implementacao de av. por demanda
             ;[(cdr) (cdrS (parse (second sl)))];removido esperando implementacao de av. por demanda
             [(display)(displayS (parse (second sl)))]
             [(quote) (quoteS (s-exp->symbol (second sl)))]
             [else (error 'parse "invalid list input")])))]
    [else (error 'parse "invalid input")]))


; Facilitator
(define (interpS [s : s-expression]) (interp (desugar (parse s)) mt-env))

; Printing
;mais um presentinho, função que imprime valores
;com  isso conseguimos ver suspensões sendo impressas de uma maneira mais bonitinha
(define (print-value [value : Value ] ) : void
                      
                      (type-case Value value
                        [numV  (n) (display n)]
                        [quoteV (symb) (display symb)]
                        [closV (arg body env)
                               (begin (display "<<")
                                      (display "lambda(")
                                      (display arg)
                                      (display ")")
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
                       
                        ;[cellV (first second)
                        ;       (begin (display "(")
                        ;              (print-list value); pequeno truque, nao olho os valores, imprimo a lista 
                        ;              (display ")")
                        ;              );removido esperando implementacao de av. por demanda
                        ;       ]
                        [nullV ()
                               (display '())]))
;para imprimir uma lista toda
(define (print-list cell) : void
  (begin 
         ;(print-value (unbox (cellV-first cell)));removido esperando implementacao de av. por demanda
         (display " ")
         ;(let ([rest (...]); vc vai precisar extrair o valor de car para imprimir
         ;  (type-case Value rest 
         ;    [nullV () (display "") ]; null at the end of the list is not printed
             ;a linha abaixo precisa ser "descomentada"quando vc implementar cellV
             ;[cellV (first second) (print-list rest)];recursão para o resto
          ;   [else (begin (display ".")
          ;              (print-value rest))])); quando cdr não aponta para outra célula
         )
  )
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
    ;[idC   (id)(display id)];removido esperando implementacao de av. por demanda
    ;[appC  (fun arg) (begin (display "(")
    ;                        (print-exp fun)
    ;                        (display " ")
    ;                        (print-exp arg)
    ;                        (display ")"))]
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
    
    ;[setC  (var arg)
    ;       (begin (display "(:= ")
    ;              (display var)
    ;              (display " ")
    ;              (print-exp arg)
    ;              (display ")"))]

    ;[letC  (name arg body) 
    ;       (begin (display "(let (( ")
    ;              (display name)
    ;              (display " ")
    ;              (print-exp arg)
    ;              (display "))")
    ;              (print-exp body))]
    ;[consC (car cdr)
    ;       (begin (display "(cons ")
    ;              (print-exp car)
    ;              (display " ")
    ;              (print-exp cdr)
    ;              (display ")"))]
    ;[carC  (cell)
    ;      (begin (display "(car ")
    ;              (print-exp cell)
    ;              (display ")"))]
    ;[cdrC  (cell)
    ;       (begin (display "(cdr ")
    ;              (print-exp cell)
    ;              (display ")"))]
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
;IMPORTANTE -- FUNCAO AUXILIAR EM BOX PARA ELIMINAR SUSPENSOES
;esta função é essencial para garantir que as suspensões, uma vez avaiadas,
;são subsituidas pelo valor resultante. Você agora, quando criar variáveis em ambientes, ou
;quando criar células, colocar um box com uma suspensionV contendo a expressão a ser avaliada e o
;ambiente
;ao acessar variáveis no ambiente (idC)  e nos campos de uma célula (carC e cdrC), você deve usar
;olha-valor-box, que será definida por você 


   
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
; Sugestões de testes

;Esta cria uma funcao recursiva fun e imprime o valor do parametro a cada chamada.
; (interpS '(letrec fun (lambda x (if x (begin (display x)
;                                              (call fun (- x 1)))
;                                         x))
;                   (call fun 8)))
; o proximo é uma lista que nao termina em celular "null"
;(interpS '(display (cons 1 (cons (quote a) (cons 5 6)))))
;agora uma lista "normal" onde o cdr da ultima celular é nulo
;(interpS '(display (cons 1 (cons 2 (cons 3 ())))))
;(interpS '(display (lambda x (+ x 2))))
;(interpS '(display (call (lambda y (lambda x (+ x y))) 5)))
; display de closV
;(interpS '(display (call (lambda y (lambda x (+ x y))) 5)))


         