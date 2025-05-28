% === Directivas ===
:- discontiguous umbral_minimo_angulo/2.
:- discontiguous umbral_maximo_angulo/2.

% === Usuarios ===
usuario(jason).
usuario(ofelia).
usuario(mariano).
usuario(alicia).
usuario(luis).
usuario(kevin).

postura_valida(kevin).
postura_valida(jason).

salud_apropiada(kevin).
salud_apropiada(jason).

% === Ejercicio único ===
ejercicio(sentadilla).

% === Tipo de ángulo asociado ===
tipo_angulo(rodilla).

% === Umbrales de ángulo para sentadilla ===
umbral_minimo_angulo(sentadilla, 80).
umbral_maximo_angulo(sentadilla, 100).

% === Niveles de usuario ===
nivel(jason, principiante).
nivel(ofelia, intermedio).
nivel(mariano, avanzado).
nivel(alicia, principiante).
nivel(luis, intermedio).
nivel(kevin, avanzado).

% === Posturas válidas ===
posicion(arriba).
posicion(abajo).

% === Retroalimentación positiva ===
retroalimentacion_correcta("¡Muy bien hecho!").
retroalimentacion_correcta("¡Buena repetición!").
retroalimentacion_correcta("¡Eso estuvo perfecto!").
retroalimentacion_correcta("¡Excelente ejecución!").
retroalimentacion_correcta("¡Correcto, sigue así!").
retroalimentacion_correcta("¡Gran esfuerzo!").
retroalimentacion_correcta("¡Buen trabajo!").
retroalimentacion_correcta("¡Sigue así!").
retroalimentacion_correcta("¡Perfecto movimiento!").
retroalimentacion_correcta("¡Muy buen ritmo!").

% === Retroalimentación visual negativa ===
retroalimentacion_incorrecta("Tu postura no es correcta. Observa el ejemplo para corregirla.").

% === Actuadores disponibles ===
actuador(voz).
actuador(digital).
actuador(gif_correctivo).  % Actuador nuevo para mostrar imagen o video de corrección

% === Recursos visuales ===
recurso_visual(sentadilla, "sentadilla_correcta.gif").

% === Reglas ===

% R1: Validar si el ángulo de sentadilla es correcto
angulo_valido_para_sentadilla(Angulo) :-
    umbral_minimo_angulo(sentadilla, Min),
    umbral_maximo_angulo(sentadilla, Max),
    Angulo >= Min,
    Angulo =< Max.

% R2: Dar retroalimentación si el ángulo es válido
retroalimentar(sentadilla, Angulo, Mensaje) :-
    angulo_valido_para_sentadilla(Angulo),
    retroalimentacion_correcta(Mensaje).

% R3: Determinar si un usuario es entrenable
usuario_entrenable(U) :-
    usuario(U),
    postura_valida(U),
    salud_apropiada(U).

% R4: Recomendación según nivel del usuario
recomendar_repeticiones(principiante, 3).
recomendar_repeticiones(intermedio, 5).
recomendar_repeticiones(avanzado, 8).

% R5: Retroalimentación visual cuando el ángulo es incorrecto
retroalimentar_visual(sentadilla, Angulo, Mensaje, Recurso) :-
    \+ angulo_valido_para_sentadilla(Angulo),
    retroalimentacion_incorrecta(Mensaje),
    recurso_visual(sentadilla, Recurso).
