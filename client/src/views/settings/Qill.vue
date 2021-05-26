<template>
  <!-- Two-way Data-Binding -->
  <div>
    <quill-editor
      ref="myQuillEditor"
      v-model="content"
      @blur="onEditorBlur($event)"
      @focus="onEditorFocus($event)"
      @ready="onEditorReady($event)"
    />

    <!-- Or manually control the data synchronization -->
    <quill-editor :content="content" :options="editorOption" @change="onEditorChange($event)" />
  </div>
</template>

<script>
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'

import { quillEditor } from 'vue-quill-editor'

export default {
  components: {
    quillEditor,
  },
}
// You can also register Quill modules in the component
import Quill from 'quill'

export default {
  data() {
    return {
      content: '<h2>I am Example</h2>',
    }
  },
  methods: {
    onEditorBlur(quill) {
      console.log('editor blur!', quill)
    },
    onEditorFocus(quill) {
      console.log('editor focus!', quill)
    },
    onEditorReady(quill) {
      console.log('editor ready!', quill)
    },
    onEditorChange({ quill, html, text }) {
      console.log('editor change!', quill, html, text)
      this.content = html
    },
  },
  computed: {
    editor() {
      return this.$refs.myQuillEditor.quill
    },
  },
  mounted() {
    console.log('this is current quill instance object', this.editor)
  },
}
</script>
