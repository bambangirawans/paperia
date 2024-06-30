import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def predict_clv(customers_df):
    # Feature engineering
    X = customers_df[['Recency', 'Frequency', 'Monetary']]
    y = customers_df['CLV']  # Assuming 'CLV' is the target variable

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a Random Forest Regressor model
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)

    return mse

def predict_churn(customers_df):
    # Assuming 'Churn' is the target variable
    X = customers_df[['Recency', 'Frequency', 'Monetary']]
    y = customers_df['Churn']

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a Random Forest Classifier model
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Make predictions
    churn_predictions = model.predict(X_test)

    return churn_predictions

def personalized_recommendations(customers_df, customer_id):
    # Assuming 'Products' is a column containing the list of products purchased by each customer
    customer_data = customers_df[customers_df['CustomerID'] == customer_id]
    products_purchased = set(customer_data['Products'].iloc[0])

    # Get similar customers (e.g., based on clustering)
    similar_customers = get_similar_customers(customers_df, customer_id)

    # Aggregate products purchased by similar customers
    similar_products = []
    for _, similar_customer in similar_customers.iterrows():
        similar_products.extend(similar_customer['Products'])

    # Filter out products already purchased by the customer
    recommendations = set(similar_products) - products_purchased

    return list(recommendations)[:5]  # Return top 5 recommendations


def process_sales_and_marketing(customers_df):
    try:
        # Customer segmentation (as shown in the previous example)
        segmented_customers = customer_segmentation(customers_df)

        # Predict CLV
        clv_error = predict_clv(segmented_customers)

        # Predict churn
        churn_predictions = predict_churn(segmented_customers)

        # Get personalized recommendations
        recommendations = personalized_recommendations(segmented_customers)

        return {
            'status': 'success',
            'data': {
                'segmented_customers': segmented_customers,
                'clv_error': clv_error,
                'churn_predictions': churn_predictions,
                'recommendations': recommendations
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


def customer_segmentation(customers_df):
    # Feature selection: Recency, Frequency, Monetary
    features = customers_df[['Recency', 'Frequency', 'Monetary']]

    # Standardize the features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Determine the optimal number of clusters using the Elbow method
    inertia = []
    for n_clusters in range(1, 11):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(scaled_features)
        inertia.append(kmeans.inertia_)

    # Assuming the optimal number of clusters is 3 (elbow point)
    n_clusters = 3
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(scaled_features)

    # Assign cluster labels to the original dataframe
    customers_df['Cluster'] = kmeans.labels_

    return customers_df

def process_sales_and_marketing_simple(customers_df):
    try:
        segmented_customers = customer_segmentation(customers_df)
        return {
            'status': 'success',
            'data': segmented_customers
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
