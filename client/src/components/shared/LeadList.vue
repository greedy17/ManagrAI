<template>
  <div class="lead-list" :class="{ dark: dark }">
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
    dark: {
      type: Boolean,
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
@import '@/styles/mixins/utils';

.lead-list {
  @include disable-text-select();
  display: flex;
  align-items: center;
  padding: 0 8px;
  width: 142px;
  height: 20px;
  border-radius: 5px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  background-color: $white;
}

.list-name {
  @include pointer-on-hover();
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
}

.remove-list-icon {
  @include pointer-on-hover();
  height: 55%;
  margin-left: auto;
}

.dark {
  background-color: $soft-gray;
}
</style>
