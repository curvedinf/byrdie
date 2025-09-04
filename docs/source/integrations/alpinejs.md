# Alpine.js Integration

Byrdie's frontend bridge is built on top of [Alpine.js](https://alpinejs.dev/), a rugged, minimal framework for composing behavior directly in your markup. Byrdie leverages Alpine.js to provide a seamless connection between your backend Python models and your frontend components.

## How Byrdie Uses Alpine.js

When you use a Byrdie component in a template (e.g., `<note />`), Byrdie automatically initializes an Alpine.js component. The data from your Python model is exposed to the Alpine component's scope, allowing you to access model fields and methods directly in your HTML.

For example, you can use Alpine's `x-data` directive to define component-specific state, `x-show` to toggle the visibility of elements, and `@click` to handle user interactions by calling methods on your Python model.

## Example

Here is an example of a Byrdie component that uses Alpine.js for in-place editing:

```html
<!-- components/note.html -->
<note x-data="{ is_editing: false, edited_text: text }">
    <!-- Show this when not editing -->
    <div x-show="!is_editing">
        <p @dblclick="is_editing = true; edited_text = text">{{ text }}</p>
    </div>

    <!-- Show this when editing -->
    <div x-show="is_editing" x-cloak>
        <input type="text" x-model="edited_text">
        <button @click="save(edited_text)">Save</button>
        <button @click="is_editing = false">Cancel</button>
    </div>

    <small>Created: {{ created_at|date:"M d, Y" }}</small>
</note>
```

In this example:
- `x-data` initializes the component's state.
- `x-show` toggles the visibility of the editing and non-editing views.
- `@dblclick` and `@click` handle user events.
- `x-model` binds the value of the input field to the `edited_text` state.
- The `save()` method is a method on the Python `Note` model that is exposed to the frontend.

## Further Reading

For more information on Alpine.js and its directives, please refer to the official [Alpine.js documentation](https://alpinejs.dev/).
