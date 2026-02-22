import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add trailing slash to all requests (prevents FastAPI 307 redirect)
apiClient.interceptors.request.use((config) => {
    if (config.url && !config.url.endsWith('/') && !config.url.includes('?')) {
        config.url += '/';
    }
    return config;
});

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);
