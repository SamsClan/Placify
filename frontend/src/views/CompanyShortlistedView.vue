<template>
  <AppLayout>
    <PageHeader
      eyebrow="Company workspace"
      title="Shortlisted candidates"
      subtitle="Candidates awaiting your final decision."
      back-to="/company/dashboard"
      back-label="Dashboard"
    />

    <SkeletonBlock v-if="loading" height="220px" border-radius="16px" />

    <StateMessage
      v-else-if="shortlisted.length === 0"
      icon="fas fa-star"
      title="No shortlisted candidates yet"
      description="Shortlist promising applicants from the Applications page to see them here."
    />

    <template v-else>
      <div class="row g-4">
        <div v-for="item in shortlisted" :key="item.id" class="col-12 col-md-6 col-lg-4">
          <div class="pp-panel py-3 h-100">
            <div class="d-flex align-items-center gap-2 mb-2">
              <EntityAvatar :name="item.student.name" :size="36" />
              <div>
                <h2 class="h6 fw-bold mb-0" style="color: var(--pp-navy)">
                  {{ item.student.name }}
                </h2>
                <div class="small text-muted">{{ item.drive.job_title }}</div>
              </div>
              <span class="badge-status badge-amber ms-auto"
                ><i class="fas fa-star" aria-hidden="true"></i>Shortlisted</span
              >
            </div>
            <div class="small text-muted">
              <i class="fas fa-comment me-1" aria-hidden="true"></i
              >{{ item.remarks || "No remarks yet." }}
            </div>
            <div class="mt-2">
              <button
                class="btn-pp-outline btn-sm w-100"
                type="button"
                @click="viewApplication(item.id)"
              >
                <i class="fas fa-eye me-1" aria-hidden="true"></i>View
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import AppLayout from "../layouts/AppLayout.vue";
import PageHeader from "../components/PageHeader.vue";
import EntityAvatar from "../components/EntityAvatar.vue";
import StateMessage from "../components/StateMessage.vue";
import SkeletonBlock from "../components/SkeletonBlock.vue";
import http from "../api/http";

const loading = ref(true);
const shortlisted = ref([]);
const router = useRouter();

onMounted(async () => {
  loading.value = true;
  try {
    const response = await http.get("/api/v1/company/shortlisted");
    shortlisted.value = response.data.shortlisted || [];
  } finally {
    loading.value = false;
  }
});

function viewApplication(id) {
  router.push(`/company/shortlisted/${id}`);
}
</script>
