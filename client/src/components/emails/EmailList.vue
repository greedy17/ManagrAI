<template>
  <div>
    <div class="email__row">
      <div class="form__element-header">{{ label }}:</div>
      <div class="email__contact-tag" v-for="contactObject in emails" :key="contactObject.email">
        {{ contactObject.email }} <span @click="removeEmail(contactObject)">&nbsp;[X]</span>
      </div>
      <span v-if="!showAddBox" @click="showEmailBox()">
        &nbsp;[ + ]
      </span>
      <span v-if="showAddBox" @click="hideEmailBoxes()">
        &nbsp;[ - ]
      </span>
    </div>
    <div class="box" v-if="showAddBox">
      <div class="box__content">
        <div class="new-email-box">
          <div class="form__element--inline">
            <div class="form__element-header">Email</div>
            <input class="form__input" type="text" v-model="newContactEmail" />
          </div>
          <div class="form__element--inline">
            <div class="form__element-header">Name</div>
            <input class="form__input" type="text" v-model="newContactName" />
          </div>
        </div>
        <div class="form__element--inline">
          <button
            class="button"
            @click="addEmail(generateContactObject(newContactName, newContactEmail))"
          >
            Add New Email
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmailList',
  props: {
    emails: {
      type: Array,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      newContactEmail: '',
      newContactName: '',
      showAddBox: false,
    }
  },
  methods: {
    hideEmailBoxes() {
      this.showAddBox = false
    },
    showEmailBox() {
      this.showAddBox = true
    },
    addEmail(contactObject) {
      this.$emit('add', contactObject)
    },
    removeEmail(contactObject) {
      this.$emit('remove', contactObject)
    },
    generateContactObject(name, email) {
      this.showAddBox = false
      return {
        name: name,
        email: email,
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers';
@import '@/styles/emails';
@import '@/styles/forms';
@import '@/styles/layout';
@import '@/styles/mixins/inputs';

.new-email-box {
  width: 100%;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
}
</style>
