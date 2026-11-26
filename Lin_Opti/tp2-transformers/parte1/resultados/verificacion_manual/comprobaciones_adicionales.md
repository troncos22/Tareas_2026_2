# Comprobaciones adicionales de la Actividad 2 (posteriores al desarrollo manual)

Generado por la sesión de infraestructura con fracciones exactas y numpy, en el contenedor `teoria`,
después de terminado el desarrollo manual. Complementa `verificacion_actividades_1_2.md`.

- M = AX = [['1/2', '-1/4'], ['0', '-1/2']]
- M^T M = [['1/4', '-1/8'], ['-1/8', '5/16']]; valores propios (numpy) = 0.152403, 0.410097
- (9 + sqrt(17))/32 = 0.410097; 2/lambda_max = 4.876894
- ||G||_F^2 = 169/256; ||AXG||_F^2 = 481/4096
- L(W_V - eta G) = L0 - eta ||G||^2 + eta^2/2 ||AXG||^2; con eta = 1/2 da 56225/32768 (= L1 del desarrollo: 56225/32768)
- Umbral exacto para que ESTE paso baje la pérdida: eta < 2||G||^2/||AXG||^2 = 416/37 ≈ 11.2432
- Reducción relativa (L0 - L1)/L0 = 15.5273 %
