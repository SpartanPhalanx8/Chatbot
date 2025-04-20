# Generate some sample data
np.random.seed(0)
X = 2 * np.random.rand(100, 1)
y = 4 + 3 * X + np.random.randn(100, 1)

# Add a column of ones to include the intercept term
X_b = np.c_[np.ones((100, 1)), X]

# Implement a simple linear regression algorithm
def linear_regression(X, y):
    theta = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)
    return theta

# Mean squared calculation
def calculate_mse(y_true, y_pred):
    return np.sum((y_true - y_pred) ** 2) / len(y_true)

# Predict using the linear regression model
theta = linear_regression(X_b, y)
y_pred = X_b.dot(theta)

# Correct mean squared error calculation for comparison
def calculate_correct_mse(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

# Calculate MSE using the faulty and correct functions
faulty_mse = calculate_faulty_mse(y, y_pred)
correct_mse = calculate_correct_mse(y, y_pred)

print("Theta (parameters):", theta)
print("Faulty MSE:", faulty_mse)
print("Correct MSE:", correct_mse)