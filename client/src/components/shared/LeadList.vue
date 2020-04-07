<template>
  <div class="lead-list">
    <span class="list-name" @click="handleNameClick">
      {{ listName }}
    </span>
    <img
      class="remove-list-icon"
      src="@/assets/images/remove.svg"
      alt="remove icon"
      @click="handleIconClick"
    />
  </div>
</template>

<script>
export default {
  name: 'LeadList',
  props: {
    listName: {
      type: String,
      required: true,
    },
  },
  data() {
    return {}
  },
  methods: {
    handleNameClick() {
      let leadListID = null
      this.$emit('clicked-list-name', leadListID)
    },
    handleIconClick() {
      let leadListID = null
      this.$emit('deleted-lead-list', leadListID)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.lead-list {
  display: flex;
  align-items: center;
  margin: 0 1vh;
  padding: 0 8px;
  width: 142px;
  height: 20px;
  border-radius: 5px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
}

.list-name {
  width: 90%;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 11px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.45;
  letter-spacing: normal;
  color: $dark-gray-blue;
  text-decoration: underline;

  &:hover {
    cursor: pointer;
  }
}

.remove-list-icon {
  height: 55%;
  margin-left: auto;

  &:hover {
    cursor: pointer;
  }
}
</style>
