<template>
  <div class="summaries">
    <div class="display-flex">
      <SummariesSinglePage
        :page="page"
        :selectedSearch="selectedSearch"
        @change-search="changeSearch"
      />
    </div>
  </div>
</template>
<script>
import PRTopBar from '@/components/pr/PRTopBar.vue'
import SummariesMainContent from '@/components/pr/SummariesMainContent.vue'
import SummariesSinglePage from '@/components/pr/SummariesSinglePage.vue'
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
        },
      ],
    }
  },
  watch: {},
  created() {},
  methods: {
    changeSearch(newSearch) {
      this.searchList.push(newSearch)
      this.selectedSearch = newSearch
    },
    changePage(page) {
      this.page = page
    },
  },
  computed: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.summaries {
  background-color: white;
  width: 100vw;
  height: 100vh;
  display: flex;
  overflow-y: scroll;
  font-family: $base-font-family;
  color: $chat-font-color;
  letter-spacing: 0.4px;
  line-height: 1.5;
  position: relative;
  @media only screen and (max-width: 600px) {
    height: 91vh;
  }
}

#main {
  flex: 1;
  width: 100vw;
  background-color: white;
  z-index: 5;
}

.elipsis-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 450px;
}

#right-sidebar {
  width: 525px;
  border-left: 1px solid rgba(0, 0, 0, 0.1);
}

// @media (max-width: 1000px) {
//   .summaries {
//     flex-direction: column;
//   }

//   #main {
//     order: 2;
//     width: 100%;
//     height: 75%;
//   }

//   #right-sidebar {
//     width: 100%;
//     height: 40%;
//     order: 1;
//     border-bottom: 1px solid rgba(0, 0, 0, 0.1);
//   }
// }
</style>