<template>
  <div class="account">
    <div class="header" @click="toggleLeads" :style="headerBorder">
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="account-title"> {{ account.name }} </span>
      <span class="leads-count"> {{ numOfLeads }} {{ numOfLeads === 1 ? 'Lead' : 'Leads' }}</span>
    </div>
    <div class="leads-container" v-if="showLeads">
      <Lead v-for="lead in account.leads" :key="lead.id" :lead="lead" />
    </div>
  </div>
</template>

<script>
import Lead from '@/components/prospect/Lead'

export default {
  name: 'Account',
  props: ['account'],
  components: {
    Lead,
  },
  data() {
    return {
      showLeads: false,
    }
  },
  methods: {
    toggleLeads() {
      this.showLeads = !this.showLeads
    },
  },
  computed: {
    numOfLeads() {
      return this.account.leads.length
    },
    headerBorder() {
      return {
        border: this.showLeads ? '2px solid #fafafa' : '2px solid white', // $off-white || $white
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.header {
  @include disable-text-select();
  @include pointer-on-hover();
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

.account-title {
  font-weight: bold;
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;
}

.leads-count {
  align-self: center;
  margin-left: 20%;
  margin-right: auto;
}

.leads-container {
  margin-left: 2%;
  margin-right: 1%;
}
</style>
