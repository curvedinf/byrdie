// Byrdie frontend bridge
document.addEventListener('alpine:init', () => {
    window.byrdie = {};

    if (window.byrdie_routes) {
        for (const [name, path] of Object.entries(window.byrdie_routes)) {
            const parts = name.split('.');
            let current = window.byrdie;
            for (let i = 0; i < parts.length - 1; i++) {
                const part = parts[i];
                if (!current[part]) {
                    current[part] = {};
                }
                current = current[part];
            }
            const finalPart = parts[parts.length - 1];

            current[finalPart] = async (params = {}) => {
                // Replace path parameters like <int:pk>
                let finalPath = path;
                const urlParams = new URLSearchParams();

                for(const [key, value] of Object.entries(params)) {
                    if(finalPath.includes(`<int:${key}>`)) {
                        finalPath = finalPath.replace(`<int:${key}>`, value);
                    } else if (finalPath.includes(`<${key}>`)) {
                        finalPath = finalPath.replace(`<${key}>`, value);
                    } else {
                        urlParams.append(key, value);
                    }
                }

                const url = new URL(finalPath, window.location.origin);
                url.search = urlParams.toString();

                const response = await fetch(url, {
                    method: 'GET', // for now, we only support GET
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') // Django's CSRF token
                    },
                    // body will be used for POST/PUT in the future
                });

                if (!response.ok) {
                    throw new Error(`Byrdie API error: ${response.statusText}`);
                }

                return response.json();
            };
        }
    }

    Alpine.data('byrdieComponent', (initialData) => {
        const component = { ...initialData };

        for (const methodName of initialData.exposed_methods) {
            component[methodName] = async (...args) => {
                const appLabel = initialData._meta.app_label;
                const modelName = initialData._meta.model_name;
                const pk = initialData.pk;

                let body = {};
                if (args.length > 0) {
                    body = args[0];
                }

                const response = await fetch(`/byrdie/call/${appLabel}/${modelName}/${pk}/${methodName}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify(body)
                });

                if (!response.ok) {
                    throw new Error(`Byrdie method call error: ${response.statusText}`);
                }

                const result = await response.json();

                // Update the component's data
                for (const [key, value] of Object.entries(result)) {
                    component[key] = value;
                }
            };
        }

        return component;
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
