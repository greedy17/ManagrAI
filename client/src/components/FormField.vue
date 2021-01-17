<template>
  <div class="form-field-container">
    <div class="field">
      <slot name="input"> </slot>
      <label :for="binding">{{ labelText }}</label>
    </div>
    <div v-if="this.showErrors" class="error">
      <span
        ><b>{{ errors.length > 0 ? errors.map(e => e.message).join(' ') : '' }}</b></span
      >
    </div>
  </div>
</template>

<script>
export default {
  name: 'FormField',
  props: {
    binding: {
      type: String,
    },
    labelText: {
      type: String,
    },
    errors: {
      type: Array,
    },
  },
  data() {
    return {
      showErrors: false,
      error: {},
    }
  },
  watch: {
    // TODO find out why it shows one by one or null
    // TODO may switch this back to the old way so as to handle server side form field errors as well or use class setter
    errors: function() {
      // this.error = this.errors.find(error => error.fieldName === this.binding)
      if (this.errors.length > 0) {
        this.showErrors = true
      } else {
        this.showErrors = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/inputs';
.form-field-container {
  width: 100%;
}
.error > span > b {
  color: red;
}
.field {
  display: flex;
  flex-flow: column-reverse;
  margin-bottom: 0.5rem;
  width: 100%;
  justify-content: space-around;
}
label,
input,
textarea {
  transition: all 0.2s;
}
label {
  opacity: 0.5;
  transition: inherit;
  font-size: 14px;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: $base-gray;
  @include base-font-styles();
}

input {
  @include input-field();
  cursor: text;
  &::-webkit-input-placeholder {
    opacity: 0;
    transition: inherit;
    font-size: 14px;
    line-height: 1.29;
    letter-spacing: 0.5px;
    color: $base-gray;
    @include base-font-styles();
  }
}
textarea {
  @include input-field();
  cursor: text;
  &::-webkit-input-placeholder {
    opacity: 0;
    transition: inherit;
    resize: none;
    height: 94%;
    flex-grow: 1;
    margin: 2% 0;
    font-size: 14px;
    @include base-font-styles();
  }
}

/**
* By default, the placeholder should be transparent. Also, it should 
* inherit the transition.
*/
::-webkit-input-placeholder {
  opacity: 0;
  transition: inherit;
}
::placeholder {
  opacity: 0;
}

input:focus,
textarea:focus {
  outline: 0;
  border-bottom: 1px solid gray;
}

/**
* Translate down and scale the label up to cover the placeholder,
* when following an input (with placeholder-shown support).
* Also make sure the label is only on one row, at max 2/3rds of the
* field—to make sure it scales properly and doesn't wrap.
*/
input:placeholder-shown + label,
textarea:placeholder-shown + label {
  cursor: text;
  max-width: 30.66%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transform-origin: left bottom;
  transform: translate(1rem, 2.6rem) scale(1);
}

/**
* Show the placeholder when the input is focused.
*/
input:focus::-webkit-input-placeholder,
textarea:focus::-webkit-input-placeholder {
  opacity: 1;
}
/**
* When the element is focused, remove the label transform.
* Also, do this when the placeholder is _not_ shown, i.e. when 
* there's something in the input at all.
*/
input:not(:placeholder-shown) + label,
textarea:not(:placeholder-shown) + label,
input:focus + label,
textarea:focus + label {
  transform: translate(0, 0) scale(1);
  cursor: pointer;
}
</style>
