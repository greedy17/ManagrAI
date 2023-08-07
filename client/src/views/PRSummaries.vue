<template>
  <div class="summaries">
    <PRTopBar :selectedSearch="selectedSearch" :searchList="searchList" @change-page="changePage" />
    <div class="display-flex">
      <SummariesSinglePage :page="page" :selectedSearch="selectedSearch" @change-search="changeSearch" />
      <!-- <SummariesMainContent /> -->
      <!-- <PRRightBar /> -->
    </div>
  </div>
</template>
<script>
import PRTopBar from '@/components/pr/PRTopBar.vue';
import SummariesMainContent from '@/components/pr/SummariesMainContent.vue';
import SummariesSinglePage from '@/components/pr/SummariesSinglePage.vue';
import PRRightBar from '@/components/pr/PRRightBar.vue'

export default {
  name: 'PRSummaries',
  components: {
    PRTopBar,
    SummariesMainContent,
    PRRightBar,
    SummariesSinglePage,
  },
  data() {
    return {
      selectedSearch: null,
      page: 'SUMMARIES',
      searchList: [
        {
          search: 'Tesla',
        }
      ],
    }
  },
  watch: {

  },
  created() {

  },
  methods: {
    changeSearch(newSearch) {
      this.searchList.push(newSearch)
      this.selectedSearch = newSearch
    },
    changePage(page) {
      this.page = page
    },
  },
  computed: {
    
  }
}
</script>
<style scoped>
  .summaries {
    margin-left: 60px;
  }
  .display-flex {
    display: flex;
  }
</style>