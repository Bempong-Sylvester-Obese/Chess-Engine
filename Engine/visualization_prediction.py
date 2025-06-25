import matplotlib.pyplot as plt

y_true = [1.2, -0.5, 0.0, 3.1, -2.3, 1.5, 0.7]
y_pred = [1.0, -0.1, -0.3, 2.5, -1.7, 2.1, 1.0]

plt.figure(figsize=(8, 6))
plt.scatter(y_true, y_pred, color='blue', alpha=0.7)
plt.plot([-10, 10], [-10, 10], color='red', linestyle='--')  # perfect prediction line
plt.xlabel('True Evaluation')
plt.ylabel('Predicted Evaluation')
plt.title('Model Evaluation: Predicted vs True')
plt.grid(True)
plt.xlim(-10, 10)
plt.ylim(-10, 10)
plt.show()
