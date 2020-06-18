<template>
  <div class="item-list">
    <div class="item-list__header">
      <span class="item-list__title">
        Pinned Notes
      </span>
    </div>
    <div class="item-list__item">
      <div class="note-header">
        <span>Primary Description</span>
        <img
          v-if="!editPrimary"
          class="edit"
          src="@/assets/images/pencil.svg"
          alt="icon"
          @click="editPrimaryDescription"
        />
      </div>
      <div v-if="!editPrimary" class="note-content">
        {{ primaryDescription || 'Not set' }}
      </div>
      <form v-else class="edit-form" @submit.prevent="updatePrimary">
        <input v-model="tempPrimary" placeholder="Not set" />
        <button type="submit">Save</button>
        <button type="reset" @click="cancelEditPrimary">Cancel</button>
      </form>
    </div>
    <div class="item-list__item">
      <div class="note-header">
        <span>Secondary Description</span>
        <img
          v-if="!editSecondary"
          class="edit"
          src="@/assets/images/pencil.svg"
          alt="icon"
          @click="editSecondaryDescription"
        />
      </div>
      <div v-if="!editSecondary" class="note-content">
        {{ secondaryDescription || 'Not set' }}
      </div>
      <form v-else class="edit-form" @submit.prevent="updateSecondary">
        <input v-model="tempSecondary" placeholder="Not set" />
        <button type="submit">Save</button>
        <button type="reset" @click="cancelEditSecondary">Cancel</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PinnedNotes',
  props: {
    primaryDescription: {
      required: true,
      type: String,
    },
    secondaryDescription: {
      required: true,
      type: String,
    },
  },
  data() {
    return {
      editPrimary: false,
      editSecondary: false,
      tempPrimary: this.primaryDescription,
      tempSecondary: this.secondaryDescription,
    }
  },
  methods: {
    editPrimaryDescription() {
      this.editPrimary = true
    },
    cancelEditPrimary() {
      this.editPrimary = false
      this.tempPrimary = this.primaryDescription
    },
    updatePrimary() {
      this.$emit('updated-primary-description', this.tempPrimary)
      this.editPrimary = false
    },
    editSecondaryDescription() {
      this.editSecondary = true
    },
    cancelEditSecondary() {
      this.editSecondary = false
      this.tempSecondary = this.primaryDescription
    },
    updateSecondary() {
      this.$emit('updated-secondary-description', this.tempSecondary)
      this.editSecondary = false
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
@import '@/styles/containers';

.pinned-notes {
  @include base-font-styles();
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  border: solid 1px $soft-gray;
  background-color: $white;
  display: flex;
  flex-flow: column;
  width: 100%;
  font-size: 14px;
  line-height: 1.14;
  color: $main-font-gray;
}

.header {
  height: 3rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  padding-left: 3%;
  font-weight: bold;
}

.note {
  display: flex;
  flex-flow: column;
  padding: 1.25rem 3%;
}

.note-header {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-bottom: 0.625rem;

  .edit {
    @include pointer-on-hover();
    margin-left: auto;
    height: 1rem;
    width: 1rem;
    opacity: 0.4;
  }
}

.note-content {
  color: rgba($color: $main-font-gray, $alpha: 0.4);
  max-width: 65rem;
  word-wrap: break-word;
}

.edit-form {
  display: flex;
  flex-flow: row;
  align-items: center;

  input {
    @include input-field();
    height: 1.5rem;
    padding-top: 1rem;
    padding-bottom: 1rem;
    width: 75%;
    margin-right: auto;
  }

  button[type='submit'] {
    @include primary-button();
    margin-right: 3%;
  }

  button[type='reset'] {
    @include secondary-button();
  }
}
</style>
