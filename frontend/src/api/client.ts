import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Barcha so'rovlar oxiriga trailing slash qo'shish (FastAPI 307 redirect oldini olish)
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
