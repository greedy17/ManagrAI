<template>
  <div class="create-list">
    <div class="list-header-look">
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <form @submit.prevent="createList">
        <input ref="input" v-model="title" type="text" placeholder="Enter List Name" />
      </form>
      <span class="list-length">No Opportunities</span>
      <button class="cancel" @click="resetForm">Cancel</button>
      <button class="save" @click="createList">Save</button>
    </div>
  </div>
</template>

<script>
import List from '@/services/lists'

export default {
  name: 'CreateList',
  data() {
    return {
      title: '',
    }
  },
  methods: {
    createList() {
      if (!this.title.length) {
        return
      }

      List.api.create(this.title).then(response => {
        this.resetForm()
        this.$refs.input.blur()
        this.$emit('list-created', response.data)
        this.$Alert.alert({
          type: 'success',
          timeout: 4000,
          message: 'Success! List created.',
        })
      })
    },
    resetForm() {
      this.title = ''
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.list-header-look {
  @include disable-text-select();
  @include base-font-styles();
  display: flex;
  flex-flow: row;
  align-items: center;
  margin: 1vh 1%;
  padding-left: 1%;
  height: 3rem;
  font-size: 14px;
  line-height: 1.14;
  color: $main-font-gray;
}

.icon {
  height: 1.625rem;
  width: 1.625rem;
  display: block;
}

form {
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;

  input {
    @include input-field();
    width: 100%;
  }
}

.list-length {
  align-self: center;
  margin-left: 20%;
  margin-right: auto;
}

.cancel {
  @include secondary-button();
  margin-right: 0.5rem;
}

.save {
  @include primary-button();
}
</style>
