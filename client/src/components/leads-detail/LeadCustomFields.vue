<template>
  <div class="custom-fields">
    Custom Fields
  </div>
</template>
<script>
export default {
  name: 'LeadCustomFields',
  components: {},
  props: {},
  data() {
    return {}
  },
  created() {},
  computed: {},
  methods: {},
}
</script>

<style scoped lang="scss">
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.custom-fields {
  @include standard-border();
  background-color: $white;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  min-height: 50rem;
  display: flex;
  flex-flow: column;
}

.custom-fields,
.custom-fields > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.875rem;
}
</style>
